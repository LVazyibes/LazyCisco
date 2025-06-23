import os
import json
import keyring
import datetime
import re

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QListWidget, QListWidgetItem, QDialog,
    QMessageBox, QListView, QMenu, QAction, QInputDialog, QSplitter,
    QTabWidget, QCheckBox, QScrollArea, QGridLayout, QSizePolicy, QSpacerItem,
    QTreeWidget, QTreeWidgetItem, QProgressBar
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QDir, pyqtSignal, QThread
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException
import keyring.errors


# ConfigManager Class
class ConfigManager:
    """
    Manages application configurations, including saving and loading switch credentials
    and application settings.
    """
    def __init__(self):
        self.app_name = "CiscoSwitchGUI"
        self.switches_file = "switches.json"
        self.settings_file = "settings.json"
        self._ensure_config_dir()
        self.settings = self._load_settings()

    def _ensure_config_dir(self):
        """Ensures the configuration directory and necessary files exist."""
        if not os.path.exists("config"):
            os.makedirs("config")
        switches_path = os.path.join("config", self.switches_file)
        if not os.path.exists(switches_path):
            with open(switches_path, 'w') as f:
                json.dump([], f)
        settings_path = os.path.join("config", self.settings_file)
        if not os.path.exists(settings_path):
            with open(settings_path, 'w') as f:
                json.dump({"open_in_new_window": False}, f, indent=4)

    def _load_settings(self):
        """Loads application settings."""
        settings_path = os.path.join("config", self.settings_file)
        try:
            with open(settings_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"open_in_new_window": False}

    def _save_settings(self):
        """Saves application settings."""
        settings_path = os.path.join("config", self.settings_file)
        with open(settings_path, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get_setting(self, key, default_value=None):
        """Retrieves a specific setting."""
        return self.settings.get(key, default_value)

    def set_setting(self, key, value):
        """Saves a specific setting."""
        self.settings[key] = value
        self._save_settings()

    def save_switch_credentials(self, ip, username, password, name=""):
        """
        Saves switch credentials (username and password to keyring, IP and name to JSON file).
        """
        try:
            # Save credentials to keyring
            keyring.set_password(self.app_name, f"{ip}_username", username)
            keyring.set_password(self.app_name, f"{ip}_password", password)

            # Load existing switches from JSON file
            switches_path = os.path.join("config", self.switches_file)
            try:
                with open(switches_path, 'r') as f:
                    switches_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                switches_data = []

            # Convert old format to new format if necessary
            if switches_data and isinstance(switches_data[0], str):
                switches_data = [{"ip": ip_addr, "name": ""} for ip_addr in switches_data]

            # Check if IP already exists and update it
            ip_exists = False
            for switch in switches_data:
                if switch["ip"] == ip:
                    switch["name"] = name
                    ip_exists = True
                    break

            # If IP doesn't exist, add it
            if not ip_exists:
                switches_data.append({"ip": ip, "name": name})

            # Save updated switches data
            with open(switches_path, 'w') as f:
                json.dump(switches_data, f, indent=4)

            print(f"DEBUG: Switch credentials saved for {ip}")
            return True

        except Exception as e:
            print(f"DEBUG: Error saving switch credentials: {str(e)}")
            return False

    def get_switch_credentials(self, ip):
        """Retrieves switch credentials from keyring."""
        try:
            username = keyring.get_password(self.app_name, f"{ip}_username")
            password = keyring.get_password(self.app_name, f"{ip}_password")
            return username, password
        except Exception as e:
            print(f"DEBUG: Error retrieving credentials for {ip}: {str(e)}")
            return None, None

    def get_saved_switches(self):
        """
        Retrieves saved switch IPs (for backward compatibility with old format).
        """
        switches_data = self.get_saved_switches_full()
        return [switch["ip"] for switch in switches_data]

    def get_saved_switches_full(self):
        """
        Retrieves full information (IP, name) of saved switches.
        Converts old IP list format to new dictionary format if necessary.
        """
        switches_path = os.path.join("config", self.switches_file)
        try:
            with open(switches_path, 'r') as f:
                switches_data = json.load(f)
                
            # Convert old format to new format if necessary
            if switches_data and isinstance(switches_data[0], str):
                switches_data = [{"ip": ip_addr, "name": ""} for ip_addr in switches_data]
                # Save in new format
                with open(switches_path, 'w') as f:
                    json.dump(switches_data, f, indent=4)
                    
            return switches_data
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def delete_switch(self, ip):
        """Deletes a switch with the given IP address."""
        try:
            # Remove from keyring
            try:
                keyring.delete_password(self.app_name, f"{ip}_username")
                keyring.delete_password(self.app_name, f"{ip}_password")
            except keyring.errors.PasswordDeleteError:
                pass  # Password was not found, which is okay

            # Remove from JSON file
            switches_path = os.path.join("config", self.switches_file)
            switches_data = self.get_saved_switches_full()
            switches_data = [switch for switch in switches_data if switch["ip"] != ip]

            with open(switches_path, 'w') as f:
                json.dump(switches_data, f, indent=4)

            print(f"DEBUG: Switch {ip} deleted successfully")
            return True

        except Exception as e:
            print(f"DEBUG: Error deleting switch {ip}: {str(e)}")
            return False

    def update_switch_name(self, ip, new_name):
        """Updates the name of a switch with the given IP address."""
        try:
            switches_path = os.path.join("config", self.switches_file)
            switches_data = self.get_saved_switches_full()
            
            for switch in switches_data:
                if switch["ip"] == ip:
                    switch["name"] = new_name
                    break

            with open(switches_path, 'w') as f:
                json.dump(switches_data, f, indent=4)

            print(f"DEBUG: Switch name updated for {ip}: {new_name}")
            return True

        except Exception as e:
            print(f"DEBUG: Error updating switch name for {ip}: {str(e)}")
            return False

    def backup_config(self, connection, ip):
        """Backs up the switch configuration."""
        try:
            config = connection.send_command("show running-config")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{ip}_{timestamp}.txt"
            
            if not os.path.exists("backups"):
                os.makedirs("backups")
            
            with open(os.path.join("backups", filename), 'w') as f:
                f.write(config)
            
            return filename
        except Exception as e:
            print(f"DEBUG: Error backing up config: {str(e)}")
            return None

    def restore_config(self, connection, filename):
        """Restores the switch configuration from a backup file."""
        try:
            with open(os.path.join("backups", filename), 'r') as f:
                config = f.read()
            
            config_lines = config.split('\n')
            connection.send_config_set(config_lines)
            return True
        except Exception as e:
            print(f"DEBUG: Error restoring config: {str(e)}")
            return False

    def save_switches_order(self, ordered_ips):
        """Saves the new order of switches to the JSON file."""
        # Get current switches data
        switches_data = self.get_saved_switches_full()
        
        # Create a dictionary for quick lookup
        switches_dict = {switch["ip"]: switch for switch in switches_data}
        
        # Create new ordered list based on the provided IP order
        new_ordered_switches = []
        for ip in ordered_ips:
            if ip in switches_dict:
                new_ordered_switches.append(switches_dict[ip])
        
        # Save the new ordered list
        with open(os.path.join("config", self.switches_file), 'w') as f:
            json.dump(new_ordered_switches, f, indent=4)
        print(f"DEBUG: Switch order saved: {ordered_ips}")


# InterfaceSearcher Class
class InterfaceSearcher:
    """
    Handles interface searching and filtering based on configuration content.
    """
    def __init__(self):
        pass

    def parse_interfaces_from_config(self, config_text):
        """
        Parses the running configuration to extract interface blocks.
        Returns a dictionary where keys are interface names and values are their configurations.
        """
        interfaces = {}
        current_interface = None
        current_config = []
        
        lines = config_text.split('\n')
        
        for line in lines:
            # Check if line starts an interface block
            if line.startswith('interface '):
                # Save previous interface if exists
                if current_interface:
                    interfaces[current_interface] = '\n'.join(current_config)
                
                # Start new interface
                current_interface = line.replace('interface ', '')
                current_config = [line]
            
            # Check if we're exiting interface configuration (next top-level command)
            elif current_interface and line and not line.startswith(' ') and not line.startswith('\t') and line.strip():
                # We've hit a new top-level command, save current interface
                interfaces[current_interface] = '\n'.join(current_config)
                current_interface = None
                current_config = []
            
            # If we're inside an interface block, add the line
            elif current_interface:
                current_config.append(line)
        
        # Save the last interface if exists
        if current_interface:
            interfaces[current_interface] = '\n'.join(current_config)
        
        return interfaces

    def search_interfaces_include(self, config_text, search_term):
        """
        Searches for interfaces that include the specified configuration.
        Returns a list of interface names that contain the search term in their configuration.
        """
        interfaces_dict = self.parse_interfaces_from_config(config_text)
        matching_interfaces = []
        
        search_term_lower = search_term.lower().strip()
        print(f"DEBUG: Searching for INCLUDE '{search_term_lower}' in {len(interfaces_dict)} interfaces")
        
        for interface_name, interface_config in interfaces_dict.items():
            if search_term_lower in interface_config.lower():
                matching_interfaces.append(interface_name)
                print(f"DEBUG: MATCH found in {interface_name}")
        
        print(f"DEBUG: Found {len(matching_interfaces)} matching interfaces for INCLUDE search")
        return matching_interfaces

    def search_interfaces_exclude(self, config_text, search_term):
        """
        Searches for interfaces that do NOT include the specified configuration.
        Returns a list of interface names that do not contain the search term in their configuration.
        """
        interfaces_dict = self.parse_interfaces_from_config(config_text)
        matching_interfaces = []
        
        search_term_lower = search_term.lower().strip()
        print(f"DEBUG: Searching for EXCLUDE '{search_term_lower}' in {len(interfaces_dict)} interfaces")
        
        for interface_name, interface_config in interfaces_dict.items():
            if search_term_lower not in interface_config.lower():
                matching_interfaces.append(interface_name)
                print(f"DEBUG: EXCLUDE match found in {interface_name}")
        
        print(f"DEBUG: Found {len(matching_interfaces)} matching interfaces for EXCLUDE search")
        return matching_interfaces


# SearchWorkerThread Class
class SearchWorkerThread(QThread):
    """
    Worker thread for performing interface search operations.
    """
    search_completed = pyqtSignal(list)
    search_error = pyqtSignal(str)
    
    def __init__(self, connection, search_term, search_mode):
        super().__init__()
        self.connection = connection
        self.search_term = search_term
        self.search_mode = search_mode
        self.interface_searcher = InterfaceSearcher()
    
    def run(self):
        """Execute the search operation in a separate thread."""
        try:
            # Get running configuration
            config_text = self.connection.send_command("show running-config")
            
            # Perform search based on mode
            if self.search_mode == 'include':
                interfaces = self.interface_searcher.search_interfaces_include(config_text, self.search_term)
            else:  # exclude
                interfaces = self.interface_searcher.search_interfaces_exclude(config_text, self.search_term)
            
            self.search_completed.emit(interfaces)
            
        except Exception as e:
            self.search_error.emit(str(e))


# SearchDialog Class
class SearchDialog(QDialog):
    """
    Dialog for interface search functionality.
    Allows users to search for interfaces based on configuration content.
    """
    interfaces_selected = pyqtSignal(list)
    
    def __init__(self, parent, connection, search_mode):
        super().__init__(parent)
        self.connection = connection
        self.search_mode = search_mode
        self.search_worker = None
        self.search_results = []
        
        self.setWindowTitle(f"Interface Search - {search_mode.title()}")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the search dialog user interface."""
        layout = QVBoxLayout()
        
        # Search input section
        search_layout = QVBoxLayout()
        if self.search_mode == 'include':
            description = "Search for text INCLUDED in interface configuration:"
            placeholder = "Example: 'switchport mode access' or 'vlan 10' configuration lines"
        else:
            description = "Search for text NOT INCLUDED in interface configuration:"
            placeholder = "Example: 'shutdown' or 'description' configuration lines"
        
        search_layout.addWidget(QLabel(description))
        
        self.search_input = QTextEdit()
        self.search_input.setMaximumHeight(100)
        self.search_input.setPlaceholderText(placeholder)
        search_layout.addWidget(self.search_input)
        
        search_button_layout = QHBoxLayout()
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        search_button_layout.addWidget(self.search_button)
        search_button_layout.addStretch()
        
        search_layout.addLayout(search_button_layout)
        layout.addLayout(search_layout)
        
        # Progress indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results section
        layout.addWidget(QLabel("Search Results:"))
        
        self.results_list = QListWidget()
        self.results_list.setSelectionMode(QListWidget.MultiSelection)
        self.results_list.itemSelectionChanged.connect(self.update_configure_button)
        layout.addWidget(self.results_list)
        
        # Selection buttons
        selection_layout = QHBoxLayout()
        
        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self.select_all_interfaces)
        selection_layout.addWidget(select_all_button)
        
        select_none_button = QPushButton("Select None")
        select_none_button.clicked.connect(self.select_no_interfaces)
        selection_layout.addWidget(select_none_button)
        
        selection_layout.addStretch()
        layout.addLayout(selection_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.configure_button = QPushButton("Configure Selected Interfaces")
        self.configure_button.setEnabled(False)
        self.configure_button.clicked.connect(self.configure_selected_interfaces)
        button_layout.addWidget(self.configure_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def perform_search(self):
        """Initiate the interface search operation."""
        search_term = self.search_input.toPlainText().strip()
        if not search_term:
            QMessageBox.warning(self, "Warning", "Please enter a search term.")
            return
        
        # Disable UI during search
        self.search_button.setEnabled(False)
        self.configure_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.results_list.clear()
        
        # Start search worker thread
        self.search_worker = SearchWorkerThread(self.connection, search_term, self.search_mode)
        self.search_worker.search_completed.connect(self.on_search_completed)
        self.search_worker.search_error.connect(self.on_search_error)
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.start()
    
    def on_search_completed(self, interfaces):
        """Handle successful search completion."""
        self.search_results = interfaces
        self.results_list.clear()
        
        if interfaces:
            for interface in interfaces:
                item = QListWidgetItem(interface)
                self.results_list.addItem(item)
        else:
            item = QListWidgetItem("No interfaces found matching the criteria")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable & ~Qt.ItemIsEnabled)
            self.results_list.addItem(item)
        
        self.update_configure_button()
    
    def on_search_error(self, error_message):
        """Handle search error."""
        QMessageBox.critical(self, "Search Error", f"Failed to perform search:\n{error_message}")
        self.results_list.clear()
    
    def on_search_finished(self):
        """Handle search thread completion."""
        self.search_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.search_worker = None
    
    def select_all_interfaces(self):
        """Select all interfaces in the results list."""
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            if item.flags() & Qt.ItemIsSelectable:
                item.setSelected(True)
        self.update_configure_button()
    
    def select_no_interfaces(self):
        """Deselect all interfaces in the results list."""
        self.results_list.clearSelection()
        self.update_configure_button()
    
    def update_configure_button(self):
        """Update the state of the configure button based on selection."""
        selected_items = self.results_list.selectedItems()
        has_valid_selection = any(item.flags() & Qt.ItemIsSelectable for item in selected_items)
        self.configure_button.setEnabled(has_valid_selection)
    
    def configure_selected_interfaces(self):
        """Emit signal with selected interfaces and close dialog."""
        selected_interfaces = []
        for item in self.results_list.selectedItems():
            if item.flags() & Qt.ItemIsSelectable:
                selected_interfaces.append(item.text())
        
        if selected_interfaces:
            self.interfaces_selected.emit(selected_interfaces)
            self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Please select at least one interface.")


# TemplateManager Class
class TemplateManager:
    """
    Manages configuration templates stored as text files.
    Supports nested directories for templates.
    """
    def __init__(self):
        self.template_dir = "conf_templates"
        self._ensure_template_dir()

    def _ensure_template_dir(self):
        """Ensures the root template directory exists."""
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)

    def _get_full_path(self, relative_path):
        """Converts a relative path to a full absolute path within the template directory."""
        return os.path.join(self.template_dir, relative_path)

    def save_template(self, relative_path, content):
        """
        Saves configuration content to a template file.
        relative_path can include directories, e.g., "group1/template_name.txt"
        """
        try:
            full_path = self._get_full_path(relative_path)
            # Ensure parent directories exist
            parent_dir = os.path.dirname(full_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            
            with open(full_path, 'w') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving template: {str(e)}")
            return False

    def load_template(self, relative_path):
        """Loads configuration content from a template file."""
        try:
            full_path = self._get_full_path(relative_path)
            with open(full_path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading template: {str(e)}")
            return None

    def list_templates(self, current_path=""):
        """
        Lists all available templates and subdirectories in a tree-like structure.
        Returns a list of dictionaries, each representing a file or folder.
        """
        template_list = []
        search_path = self._get_full_path(current_path) if current_path else self.template_dir
        
        try:
            if not os.path.exists(search_path):
                return template_list
                
            for item in sorted(os.listdir(search_path)):
                item_path = os.path.join(search_path, item)
                relative_path = os.path.join(current_path, item) if current_path else item
                
                if os.path.isdir(item_path):
                    # It's a directory
                    template_list.append({
                        'name': item,
                        'type': 'directory',
                        'path': relative_path,
                        'children': self.list_templates(relative_path)
                    })
                elif item.endswith('.txt'):
                    # It's a template file
                    template_list.append({
                        'name': item,
                        'type': 'file',
                        'path': relative_path
                    })
        except Exception as e:
            print(f"Error listing templates: {str(e)}")
            
        return template_list

    def delete_template(self, relative_path):
        """Deletes a template file or an empty directory."""
        try:
            full_path = self._get_full_path(relative_path)
            if os.path.isfile(full_path):
                os.remove(full_path)
                return True
            elif os.path.isdir(full_path):
                os.rmdir(full_path)  # Only removes empty directories
                return True
            return False
        except Exception as e:
            print(f"Error deleting template: {str(e)}")
            return False

    def rename_template(self, old_relative_path, new_relative_path):
        """Renames a template file or directory."""
        try:
            old_full_path = self._get_full_path(old_relative_path)
            new_full_path = self._get_full_path(new_relative_path)
            
            # Ensure parent directory of new path exists
            parent_dir = os.path.dirname(new_full_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            
            os.rename(old_full_path, new_full_path)
            return True
        except Exception as e:
            print(f"Error renaming template: {str(e)}")
            return False


# InterfaceListItemWidget Class
class InterfaceListItemWidget(QWidget):
    """
    A custom widget for displaying an interface in the QListWidget, including a checkbox
    and status icon.
    """
    def __init__(self, interface_name, status_icon, parent=None):
        super().__init__(parent)
        
        # Create a horizontal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 2, 4, 2)  # Reduce margins for compact appearance
        
        # Create checkbox
        self.checkbox = QCheckBox()
        layout.addWidget(self.checkbox)
        
        # Create status icon label
        self.status_label = QLabel()
        self.status_label.setPixmap(status_icon.pixmap(16, 16))  # Set icon size
        layout.addWidget(self.status_label)
        
        # Create interface name label
        self.name_label = QLabel(interface_name)
        layout.addWidget(self.name_label)
        
        # Add stretch to push everything to the left
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Store interface name for external access
        self.interface_name = interface_name

    def get_interface_name(self):
        """Returns the name of the interface."""
        return self.interface_name

    def is_checked(self):
        """Returns True if the checkbox is checked, False otherwise."""
        return self.checkbox.isChecked()

    def set_checked(self, checked):
        """Sets the checked state of the checkbox."""
        self.checkbox.setChecked(checked)
        
    def get_checkbox(self):
        """Returns the QCheckBox object for external signal connections."""
        return self.checkbox


# TemplateSelectionDialog Class
class TemplateSelectionDialog(QDialog):
    """
    A dialog for selecting a template from a list of available templates.
    Now uses a QTreeWidget for hierarchical display.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Template")
        self.setModal(True)
        self.resize(400, 300)
        
        self.template_manager = TemplateManager()
        self.selected_template = None
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Select template to use:"))
        
        # Use QTreeWidget for hierarchical display
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Templates")
        self.tree_widget.itemClicked.connect(self._select_item)
        self.tree_widget.itemDoubleClicked.connect(self._handle_double_click)
        layout.addWidget(self.tree_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)
        button_layout.addWidget(self.ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.load_templates()

    def _add_tree_items(self, parent_item, data_list):
        """Recursively adds items to the QTreeWidget."""
        for item_data in data_list:
            tree_item = QTreeWidgetItem(parent_item)
            tree_item.setText(0, item_data['name'])
            tree_item.setData(0, Qt.UserRole, item_data)
            
            if item_data['type'] == 'directory':
                # Add children recursively
                self._add_tree_items(tree_item, item_data['children'])
            elif item_data['type'] == 'file':
                # Make file items selectable (visually different)
                tree_item.setData(0, Qt.UserRole + 1, 'selectable')

    def load_templates(self):
        """Loads template names and directories into the tree widget."""
        self.tree_widget.clear()
        templates_data = self.template_manager.list_templates()
        self._add_tree_items(self.tree_widget, templates_data)
        self.tree_widget.expandAll()

    def _select_item(self, item, column):
        """Handles single click to select an item."""
        item_data = item.data(0, Qt.UserRole)
        if item_data and item_data['type'] == 'file':
            self.selected_template = item_data['path']
            self.ok_button.setEnabled(True)
        else:
            self.selected_template = None
            self.ok_button.setEnabled(False)

    def _handle_double_click(self, item, column):
        """Handles double click: expand/collapse directory or select file."""
        item_data = item.data(0, Qt.UserRole)
        if item_data and item_data['type'] == 'file':
            self.selected_template = item_data['path']
            self.accept()
        else:
            # Toggle expansion for directories
            item.setExpanded(not item.isExpanded())

    def accept(self):
        """Handles template selection and closes the dialog."""
        if self.selected_template:
            super().accept()
        else:
            QMessageBox.warning(self, "Warning", "Please select a template.")

    def get_selected_template(self):
        """Returns the full relative path of the selected template."""
        return self.selected_template


# TemplateManagerDialog Class
class TemplateManagerDialog(QDialog):
    """
    A dialog for managing (viewing, editing, deleting, renaming, adding new) configuration templates.
    Now uses a QTreeWidget for hierarchical display.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Template Management")
        self.setModal(True)
        self.resize(800, 600)
        
        self.template_manager = TemplateManager()
        self.current_template = None
        
        layout = QHBoxLayout()
        
        # Left side: Template tree and management buttons
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("Templates:"))
        
        # Template tree
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Templates and Folders")
        self.tree_widget.itemClicked.connect(self.display_selected_template_content)
        self.tree_widget.itemDoubleClicked.connect(self.expand_or_display)
        left_layout.addWidget(self.tree_widget)
        
        # Management buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("New Template")
        add_button.clicked.connect(self.add_new_template)
        button_layout.addWidget(add_button)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_selected_template)
        button_layout.addWidget(delete_button)
        
        rename_button = QPushButton("Rename")
        rename_button.clicked.connect(self.rename_selected_template)
        button_layout.addWidget(rename_button)
        
        left_layout.addLayout(button_layout)
        
        # Right side: Template content editor
        right_layout = QVBoxLayout()
        
        right_layout.addWidget(QLabel("Template Content:"))
        
        self.content_area = QTextEdit()
        self.content_area.setPlaceholderText("Select a template or create a new one...")
        right_layout.addWidget(self.content_area)
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_edited_template)
        right_layout.addWidget(save_button)
        
        # Add left and right layouts to main layout
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 2)
        
        # Close button
        close_layout = QVBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_layout.addWidget(close_button)
        close_layout.addStretch()
        
        layout.addLayout(close_layout)
        
        self.setLayout(layout)
        
        self.load_templates()

    def add_new_template(self):
        """Prompts for a new template name and creates an empty template file."""
        template_name, ok = QInputDialog.getText(self, "New Template", "Enter template name (e.g., folder/name.txt):")
        if ok and template_name:
            if not template_name.endswith('.txt'):
                template_name += '.txt'
            
            # Create empty template
            if self.template_manager.save_template(template_name, ""):
                self.load_templates()
                QMessageBox.information(self, "Success", f"Template '{template_name}' created!")
            else:
                QMessageBox.critical(self, "Error", f"Failed to create template: {template_name}")

    def load_templates(self):
        """Loads template names and directories into the tree widget."""
        self.tree_widget.clear()
        templates_data = self.template_manager.list_templates()
        self._add_tree_items(self.tree_widget, templates_data)
        self.tree_widget.expandAll()

    def _add_tree_items(self, parent_item, data_list):
        """Recursively adds items to the QTreeWidget."""
        for item_data in data_list:
            tree_item = QTreeWidgetItem(parent_item)
            tree_item.setText(0, item_data['name'])
            tree_item.setData(0, Qt.UserRole, item_data)
            
            if item_data['type'] == 'directory':
                # Add children recursively
                self._add_tree_items(tree_item, item_data['children'])

    def expand_or_display(self, item, column):
        """Handles double-click: expand/collapse directory or display file content."""
        item_data = item.data(0, Qt.UserRole)
        if item_data and item_data['type'] == 'file':
            # Display file content
            self.display_selected_template_content(item, column)
        else:
            # Toggle expansion for directories
            item.setExpanded(not item.isExpanded())

    def display_selected_template_content(self, item, column=0):
        """Displays the content of the selected template file."""
        item_data = item.data(0, Qt.UserRole)
        if item_data and item_data['type'] == 'file':
            template_path = item_data['path']
            content = self.template_manager.load_template(template_path)
            if content is not None:
                self.content_area.setPlainText(content)
                self.current_template = template_path
            else:
                self.content_area.setPlainText("Failed to load template.")
                self.current_template = None
        else:
            self.content_area.setPlainText("")
            self.current_template = None

    def save_edited_template(self):
        """Saves the edited content of the currently displayed template."""
        if self.current_template:
            content = self.content_area.toPlainText()
            if self.template_manager.save_template(self.current_template, content):
                QMessageBox.information(self, "Success", "Template saved!")
            else:
                QMessageBox.critical(self, "Error", "Failed to save template!")
        else:
            QMessageBox.warning(self, "Warning", "Please select a template to save.")

    def delete_selected_template(self):
        """Deletes the selected template file or empty directory."""
        current_item = self.tree_widget.currentItem()
        if current_item:
            item_data = current_item.data(0, Qt.UserRole)
            if item_data:
                reply = QMessageBox.question(self, "Delete Confirmation", 
                                           f"Are you sure you want to delete '{item_data['name']}'?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    if self.template_manager.delete_template(item_data['path']):
                        self.load_templates()
                        self.content_area.setPlainText("")
                        self.current_template = None
                        QMessageBox.information(self, "Success", "Item deleted!")
                    else:
                        QMessageBox.critical(self, "Error", "Failed to delete item!")
        else:
            QMessageBox.warning(self, "Warning", "Please select an item to delete.")

    def rename_selected_template(self):
        """Renames the selected template file or directory."""
        current_item = self.tree_widget.currentItem()
        if current_item:
            item_data = current_item.data(0, Qt.UserRole)
            if item_data:
                old_name = item_data['name']
                new_name, ok = QInputDialog.getText(self, "Rename", f"New name for '{old_name}':", QLineEdit.Normal, old_name)
                if ok and new_name and new_name != old_name:
                    # Build new path
                    old_path = item_data['path']
                    parent_path = os.path.dirname(old_path)
                    new_path = os.path.join(parent_path, new_name) if parent_path else new_name
                    
                    if self.template_manager.rename_template(old_path, new_path):
                        self.load_templates()
                        if self.current_template == old_path:
                            self.current_template = new_path
                        QMessageBox.information(self, "Success", "Item renamed!")
                    else:
                        QMessageBox.critical(self, "Error", "Failed to rename item!")
        else:
            QMessageBox.warning(self, "Warning", "Please select an item to rename.")


# InterfaceConfigDialog Class
class InterfaceConfigDialog(QDialog):
    """
    A dialog for configuring a specific network interface.
    """
    def __init__(self, connection, interface, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.interface = interface
        self.template_manager = TemplateManager()
        
        self.setWindowTitle(f"{interface} Configuration")
        self.setModal(True)
        self.resize(600, 400)
        
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Interface info
        info_label = QLabel(f"Interface: {self.interface}")
        info_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # Template selection button
        template_button = QPushButton("Load from Template")
        template_button.clicked.connect(self.load_template_to_config_area)
        layout.addWidget(template_button)

        # Configuration area
        layout.addWidget(QLabel("Configuration Commands:"))
        self.config_area = QTextEdit()
        self.config_area.setPlaceholderText("Enter interface configuration commands here...")
        layout.addWidget(self.config_area)

        # Buttons
        button_layout = QHBoxLayout()
        
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.apply_configuration)
        button_layout.addWidget(apply_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_template_to_config_area(self):
        """Opens TemplateSelectionDialog and loads selected template content into config_area."""
        template_dialog = TemplateSelectionDialog(self)
        if template_dialog.exec_() == QDialog.Accepted:
            selected_template = template_dialog.get_selected_template()
            if selected_template:
                template_content = self.template_manager.load_template(selected_template)
                if template_content:
                    self.config_area.setPlainText(template_content)
                else:
                    QMessageBox.critical(self, "Error", "Failed to load template!")

    def apply_configuration(self):
        """Applies the entered configuration commands to the interface."""
        config_text = self.config_area.toPlainText().strip()
        if not config_text:
            QMessageBox.warning(self, "Warning", "Please enter configuration commands.")
            return

        try:
            commands = [f"interface {self.interface}"] + config_text.split('\n') + ["exit"]
            output = self.connection.send_config_set(commands)
            QMessageBox.information(self, "Success", f"Configuration applied to {self.interface}!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error applying configuration: {str(e)}")


def parse_interface_for_range(interface_name):
    """
    Parses an interface name into components suitable for an 'interface range' command.
    Returns (full_type_name, module_part, port_number).
    Example: "GigabitEthernet1/0/1" -> ("GigabitEthernet", "1/0", 1)
             "Fa0/1"              -> ("FastEthernet", "0", 1)
             "Loopback0"          -> ("Loopback", "", 0)
    """
    # Common interface type mappings
    type_mappings = {
        'Gi': 'GigabitEthernet',
        'Fa': 'FastEthernet',
        'Et': 'Ethernet',
        'Se': 'Serial',
        'Lo': 'Loopback',
        'Vl': 'Vlan',
        'Tu': 'Tunnel'
    }
    
    # Regular expression to parse interface names
    # Matches: Type + module/slot/port or Type + number
    pattern = r'^([A-Za-z]+)(\d+(?:/\d+)*(?:/\d+)?)$'
    match = re.match(pattern, interface_name)
    
    if not match:
        return interface_name, "", 0  # Return as-is if can't parse
    
    type_part = match.group(1)
    number_part = match.group(2)
    
    # Expand abbreviated type names
    full_type = type_mappings.get(type_part, type_part)
    
    # Split the number part to get module and port
    if '/' in number_part:
        parts = number_part.split('/')
        if len(parts) >= 2:
            module_part = '/'.join(parts[:-1])
            try:
                port_number = int(parts[-1])
            except ValueError:
                port_number = 0
        else:
            module_part = ""
            try:
                port_number = int(number_part)
            except ValueError:
                port_number = 0
    else:
        module_part = ""
        try:
            port_number = int(number_part)
        except ValueError:
            port_number = 0
    
    return full_type, module_part, port_number


def create_interface_range_string(selected_interfaces):
    """
    Generates an 'interface range' command string from a list of interface names.
    Groups contiguous interfaces into ranges.
    """
    if not selected_interfaces:
        return ""
    
    if len(selected_interfaces) == 1:
        return f"interface {selected_interfaces[0]}"
    
    # Group interfaces by type and module
    interface_groups = {}
    
    for interface in selected_interfaces:
        # Parse interface name (e.g., "GigabitEthernet1/0/1" -> "GigabitEthernet", "1/0", 1)
        full_type, module_part, port_number = parse_interface_for_range(interface)
        
        # Create group key
        group_key = (full_type, module_part)
        if group_key not in interface_groups:
            interface_groups[group_key] = []
        
        interface_groups[group_key].append(port_number)
    
    # Build range strings for each group
    range_parts = []
    
    for (interface_type, module_part), ports in interface_groups.items():
        # Sort ports numerically
        ports.sort()
        
        # Create contiguous ranges
        ranges = []
        start = ports[0]
        end = ports[0]
        
        for i in range(1, len(ports)):
            if ports[i] == end + 1:
                # Contiguous port, extend range
                end = ports[i]
            else:
                # Gap found, save current range and start new one
                ranges.append((start, end))
                start = ports[i]
                end = ports[i]
        
        # Add the last range
        ranges.append((start, end))
        
        # Format ranges for this interface type
        for start_port, end_port in ranges:
            if module_part:
                # Interface with module (e.g., GigabitEthernet1/0/1)
                if start_port == end_port:
                    range_parts.append(f"{interface_type}{module_part}/{start_port}")
                else:
                    range_parts.append(f"{interface_type}{module_part}/{start_port}-{end_port}")
            else:
                # Interface without module (e.g., Loopback1)
                if start_port == end_port:
                    range_parts.append(f"{interface_type}{start_port}")
                else:
                    range_parts.append(f"{interface_type}{start_port}-{end_port}")
    
    # Join all range parts
    return f"interface range {', '.join(range_parts)}"


def _format_group_to_range_string(group):
    """
    Formats a contiguous group of interfaces into a Cisco 'interface range' compatible string.
    Group format: [(port_number, original_name), ...]
    """
    if len(group) == 1:
        # Single interface - return original name
        return group[0][1]  # group[0] is (port_number, original_name)
    
    # For multiple interfaces, try to create a range
    # Just return comma-separated list for now to avoid parsing errors
    interface_names = [item[1] for item in group]  # Extract original names
    return ', '.join(interface_names)


# BulkInterfaceConfigDialog Class
class BulkInterfaceConfigDialog(QDialog):
    """
    A dialog for applying configuration commands to multiple selected interfaces.
    """
    def __init__(self, connection, interfaces, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.interfaces = interfaces
        self.template_manager = TemplateManager()
        
        self.setWindowTitle("Bulk Interface Configuration")
        self.setModal(True)
        self.resize(600, 400)
        
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Selected interfaces info
        info_label = QLabel(f"Selected Interfaces: {len(self.interfaces)}")
        info_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # Show selected interfaces
        interface_list_label = QLabel("Selected Interfaces:")
        layout.addWidget(interface_list_label)
        
        interface_display = QTextEdit()
        interface_display.setPlainText('\n'.join(self.interfaces))
        interface_display.setMaximumHeight(100)
        interface_display.setReadOnly(True)
        layout.addWidget(interface_display)

        # Template selection button
        template_button = QPushButton("Load from Template")
        template_button.clicked.connect(self.load_template_to_config_area_bulk)
        layout.addWidget(template_button)

        # Configuration area
        layout.addWidget(QLabel("Configuration Commands:"))
        self.config_area = QTextEdit()
        self.config_area.setPlaceholderText("Enter configuration commands to apply to all selected interfaces...")
        layout.addWidget(self.config_area)

        # Buttons
        button_layout = QHBoxLayout()
        
        apply_button = QPushButton("Apply to All")
        apply_button.clicked.connect(self.apply_bulk_configuration)
        button_layout.addWidget(apply_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_template_to_config_area_bulk(self):
        """Opens TemplateSelectionDialog and loads selected template content into config_area."""
        template_dialog = TemplateSelectionDialog(self)
        if template_dialog.exec_() == QDialog.Accepted:
            selected_template = template_dialog.get_selected_template()
            if selected_template:
                template_content = self.template_manager.load_template(selected_template)
                if template_content:
                    self.config_area.setPlainText(template_content)
                else:
                    QMessageBox.critical(self, "Error", "Failed to load template!")

    def apply_bulk_configuration(self):
        """Applies the entered configuration commands to all selected interfaces using interface range."""
        config_text = self.config_area.toPlainText().strip()
        if not config_text:
            QMessageBox.warning(self, "Warning", "Please enter configuration commands.")
            return

        try:
            # Generate interface range command
            range_command = create_interface_range_string(self.interfaces)
            print(f"DEBUG: Generated range command: {range_command}")
            
            # Prepare configuration commands
            config_lines = config_text.split('\n')
            commands = [range_command] + config_lines + ["exit"]
            
            print(f"DEBUG: Applying commands: {commands}")
            
            # Apply configuration using interface range
            output = self.connection.send_config_set(commands)
            
            print(f"DEBUG: Configuration output: {output}")
            
            QMessageBox.information(self, "Success", 
                                  f"Configuration applied to {len(self.interfaces)} interfaces!\n\n"
                                  f"Command used: {range_command}")
            self.accept()
            
        except Exception as e:
            print(f"DEBUG: Error in bulk configuration: {str(e)}")
            QMessageBox.critical(self, "Error", 
                               f"Error applying bulk configuration: {str(e)}\n\n"
                               f"Command attempted: {range_command if 'range_command' in locals() else 'Unknown'}")


# GlobalConfigDialog Class
class GlobalConfigDialog(QDialog):
    """
    A dialog for applying global configuration commands to the switch.
    """
    def __init__(self, connection, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.template_manager = TemplateManager()
        
        self.setWindowTitle("Global Configuration")
        self.setModal(True)
        self.resize(600, 400)
        
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Info
        info_label = QLabel("Global Configuration Commands")
        info_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # Template selection button
        template_button = QPushButton("Load from Template")
        template_button.clicked.connect(self.load_template_to_config_area)
        layout.addWidget(template_button)

        # Configuration area
        layout.addWidget(QLabel("Configuration Commands:"))
        self.config_area = QTextEdit()
        self.config_area.setPlaceholderText("Enter global configuration commands here ('configure terminal' will be added automatically)...")
        layout.addWidget(self.config_area)

        # Console output area
        layout.addWidget(QLabel("Console Output:"))
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setMaximumHeight(150)
        layout.addWidget(self.console_output)

        # Buttons
        button_layout = QHBoxLayout()
        
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.apply_configuration)
        button_layout.addWidget(apply_button)
        
        cancel_button = QPushButton("Close")
        cancel_button.clicked.connect(self.accept)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_template_to_config_area(self):
        """Opens TemplateSelectionDialog and loads selected template content into config_area."""
        template_dialog = TemplateSelectionDialog(self)
        if template_dialog.exec_() == QDialog.Accepted:
            selected_template = template_dialog.get_selected_template()
            if selected_template:
                template_content = self.template_manager.load_template(selected_template)
                if template_content:
                    self.config_area.setPlainText(template_content)
                else:
                    QMessageBox.critical(self, "Error", "Failed to load template!")

    def apply_configuration(self):
        """Applies the entered global configuration commands."""
        config_text = self.config_area.toPlainText().strip()
        if not config_text:
            QMessageBox.warning(self, "Warning", "Please enter configuration commands.")
            return

        try:
            commands = config_text.split('\n')
            self.console_output.append(f"> Applying {len(commands)} commands...")
            
            output = self.connection.send_config_set(commands)
            self.console_output.append(f"> Configuration applied successfully!")
            self.console_output.append(f"> Output:\n{output}")
            
            QMessageBox.information(self, "Success", "Global configuration applied!")
            
        except Exception as e:
            self.console_output.append(f"> Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error applying configuration: {str(e)}")


# SwitchTabWidget Class - Content of the Tabs
class SwitchTabWidget(QWidget):
    """
    Tabbed widget representing each switch connection.
    Contains the functionality for the right and middle parts of the CiscoSwitchGUI.
    """
    def __init__(self, ip, username, password, parent=None):
        super().__init__(parent)
        self.ip = ip
        self.username = username
        self.password = password
        self.connection = None
        self.config_manager = ConfigManager()
        self.template_manager = TemplateManager()

        self.initUI()
        self.connect_to_switch()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        middle_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Middle Section (Interface/VLAN List and Information)
        list_display_layout = QHBoxLayout()

        interface_v_layout = QVBoxLayout()
        
        gigabit_checkbox_layout = QHBoxLayout()
        self.gigabit_checkbox = QCheckBox("Select All Gigabit Interfaces")
        self.gigabit_checkbox.stateChanged.connect(self.toggle_gigabit_selection)
        gigabit_checkbox_layout.addWidget(self.gigabit_checkbox)
        gigabit_checkbox_layout.addStretch(1)
        interface_v_layout.addLayout(gigabit_checkbox_layout)
        
        interface_v_layout.addWidget(QLabel('Interface List'))
        self.interface_list = QListWidget()
        self.interface_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.interface_list.customContextMenuRequested.connect(self.show_context_menu)
        self.interface_list.itemDoubleClicked.connect(self.open_interface_config)
        self.interface_list.itemClicked.connect(self.show_interface_details)
        self.interface_list.itemSelectionChanged.connect(self.update_bulk_apply_button)
        interface_v_layout.addWidget(self.interface_list)

        list_display_layout.addLayout(interface_v_layout)

        vlan_v_layout = QVBoxLayout()
        vlan_v_layout.addWidget(QLabel('VLAN List'))
        self.vlan_list = QListWidget()
        self.vlan_list.itemClicked.connect(self.show_vlan_ports)
        vlan_v_layout.addWidget(self.vlan_list)

        list_display_layout.addLayout(vlan_v_layout)
        middle_layout.addLayout(list_display_layout)

        # Interface info display
        self.interface_info = QTextEdit()
        self.interface_info.setReadOnly(True)
        self.interface_info.setMaximumHeight(200)
        
        # Middle splitter for interface/VLAN info
        self.middle_splitter = QSplitter(Qt.Vertical)
        info_container_widget = QWidget()
        info_layout = QVBoxLayout(info_container_widget)
        info_layout.setContentsMargins(0,0,0,0)
        info_layout.addWidget(QLabel('Selected Interface/VLAN Information'))
        info_layout.addWidget(self.interface_info)
        self.middle_splitter.addWidget(info_container_widget)
        
        middle_layout.addWidget(self.middle_splitter)

        self.bulk_apply_button = QPushButton("Apply Configuration to Selected")
        self.bulk_apply_button.clicked.connect(self.open_bulk_interface_config)
        self.bulk_apply_button.setEnabled(False)
        middle_layout.addWidget(self.bulk_apply_button)

        # Right Section (Command Area, Output, Backup, Global Config)
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        right_layout.addWidget(self.output_area)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter single command and press Enter (use 'Apply Global Config' for configuration)...")
        self.command_input.returnPressed.connect(self.execute_command)
        self.command_input.setEnabled(False)
        right_layout.addWidget(self.command_input)

        # Interface Search Controls
        search_layout = QHBoxLayout()
        
        self.search_interface_checkbox = QCheckBox("Search Interface")
        self.search_interface_checkbox.stateChanged.connect(self.on_search_interface_changed)
        self.search_interface_checkbox.setEnabled(False)
        search_layout.addWidget(self.search_interface_checkbox)
        
        self.inc_checkbox = QCheckBox("inc")
        self.inc_checkbox.stateChanged.connect(self.on_inc_checkbox_changed)
        self.inc_checkbox.setEnabled(False)
        search_layout.addWidget(self.inc_checkbox)
        
        self.exc_checkbox = QCheckBox("exc")
        self.exc_checkbox.stateChanged.connect(self.on_exc_checkbox_changed)
        self.exc_checkbox.setEnabled(False)
        search_layout.addWidget(self.exc_checkbox)
        
        search_layout.addStretch()
        right_layout.addLayout(search_layout)

        self.backup_button = QPushButton('Backup')
        self.backup_button.clicked.connect(self.backup_current_config)
        self.backup_button.setEnabled(False)
        right_layout.addWidget(self.backup_button)

        self.apply_global_config_button = QPushButton('Apply Global Config')
        self.apply_global_config_button.clicked.connect(self.open_global_config_dialog)
        self.apply_global_config_button.setEnabled(False)
        right_layout.addWidget(self.apply_global_config_button)

        main_layout.addLayout(middle_layout, 2)
        main_layout.addLayout(right_layout, 2)

        self.setLayout(main_layout)

    def show_context_menu(self, position):
        """Displays a context menu for interface list items."""
        selected_item = self.interface_list.itemAt(position)
        if selected_item:
            custom_widget = self.interface_list.itemWidget(selected_item)
            if custom_widget:
                interface_name = custom_widget.get_interface_name()
                context_menu = QMenu(self)
                
                default_action = QAction(f"Default {interface_name}", self)
                default_action.triggered.connect(lambda: self.default_interface(interface_name))
                context_menu.addAction(default_action)

                add_template_action = QAction(f"Add to Template", self)
                add_template_action.triggered.connect(lambda: self.add_interface_to_template(interface_name))
                context_menu.addAction(add_template_action)
                
                context_menu.exec_(self.interface_list.viewport().mapToGlobal(position))

    def add_interface_to_template(self, interface_name):
        """Fetches interface config and saves it as a template."""
        if self.connection:
            try:
                config_output = self.connection.send_command(f"show running-config interface {interface_name}")
                
                template_name, ok = QInputDialog.getText(self, "Add to Template", 
                                                         f"Enter a name for the template (e.g., folder/name):", 
                                                         QLineEdit.Normal, interface_name.replace("/", "_").replace(" ", "_"))
                if ok and template_name:
                    if not template_name.endswith(".txt"):
                        template_name += ".txt"

                    if self.template_manager.save_template(template_name, config_output):
                        QMessageBox.information(self, "Success", f"Interface configuration saved as template '{template_name}'!")
                    else:
                        QMessageBox.critical(self, "Error", f"Error saving template: {template_name}")
                elif not template_name and ok:
                    QMessageBox.warning(self, "Warning", "Template name cannot be empty.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error getting interface configuration: {str(e)}")
        else:
            QMessageBox.warning(self, "Warning", "Please connect to a switch first!")


    def default_interface(self, interface_name):
        """Resets the selected interface to its default configuration."""
        if self.connection:
            reply = QMessageBox.question(self, 'Default Interface', f'Are you sure you want to reset interface "{interface_name}" to default settings?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    commands = [
                        "configure terminal",
                        f"default interface {interface_name}",
                        "end"
                    ]
                    output = self.connection.send_config_set(commands)
                    self.output_area.append(f'\n> default interface {interface_name}\n{output}')
                    QMessageBox.information(self, "Success", f"Interface {interface_name} reset to default settings.")
                    self.load_interfaces()
                except Exception as e:
                    self.output_area.append(f'Error: {str(e)}')
                    QMessageBox.critical(self, "Error", f"Error resetting interface: {str(e)}")
        else:
            QMessageBox.warning(self, "Warning", "Please connect to a switch first!")

    def connect_to_switch(self):
        """Establishes an SSH connection to the switch using Netmiko."""
        print(f"DEBUG: Attempting to connect to {self.ip}...")
        if self.connection:
            print(f"DEBUG: Already connected to {self.ip}.")
            self.output_area.append(f'Warning: Already connected to {self.ip}.')
            return

        self.device = {
            'device_type': 'cisco_ios',
            'host': self.ip,
            'username': self.username,
            'password': self.password,
            'timeout': 10
        }

        try:
            print("DEBUG: Calling ConnectHandler...")
            self.connection = ConnectHandler(**self.device)
            print("DEBUG: ConnectHandler successful.")
            self.output_area.append('Connection successful!')
            self.command_input.setEnabled(True)
            self.backup_button.setEnabled(True)
            self.apply_global_config_button.setEnabled(True)
            self.bulk_apply_button.setEnabled(True)
            self.gigabit_checkbox.setEnabled(True)
            self.search_interface_checkbox.setEnabled(True)

            print("DEBUG: Fetching hostname...")
            hostname_output = self.connection.send_command("show running-config | include hostname")
            print(f"DEBUG: Hostname raw output: {hostname_output.strip()}") # More specific debug

            hostname = ""
            if "hostname" in hostname_output:
                hostname = hostname_output.split("hostname")[1].strip()
            
            if hostname:
                print(f"DEBUG: Hostname parsed: {hostname}")
                parent_tab_widget = self.parentWidget()
                if parent_tab_widget and isinstance(parent_tab_widget, QTabWidget):
                    tab_index = parent_tab_widget.indexOf(self)
                    if tab_index != -1:
                        parent_tab_widget.setTabText(tab_index, f"{self.ip} ({hostname})")
                        print(f"DEBUG: Tab text updated to: {self.ip} ({hostname})")

            print("DEBUG: Loading interfaces and VLANs...")
            self.load_interfaces()
            self.load_vlans()
            print("DEBUG: Connection process completed successfully.")

        except NetmikoAuthenticationException:
            error_msg = f"Authentication error: {self.ip}"
            print(f"DEBUG: {error_msg}")
            self.output_area.append(error_msg)
        except NetmikoTimeoutException:
            error_msg = f"Connection timeout: {self.ip}"
            print(f"DEBUG: {error_msg}")
            self.output_area.append(error_msg)
        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            print(f"DEBUG: {error_msg}")
            self.output_area.append(error_msg)

    def disconnect_from_switch(self):
        """Disconnects from the switch. This method should only be called automatically when the tab is closed."""
        if self.connection:
            try:
                print(f"DEBUG: Disconnecting from {self.ip}...")
                self.connection.disconnect()
                print(f"DEBUG: Successfully disconnected from {self.ip}.")
            except Exception as e:
                print(f"DEBUG: Error during disconnect from {self.ip}: {str(e)}")
            finally:
                self.connection = None

    def clear_network_info_displays(self):
        """Clears interface and VLAN lists and information display."""
        self.interface_list.clear()
        self.vlan_list.clear()
        if hasattr(self, 'interface_info'):
            self.interface_info.clear()

    def backup_current_config(self):
        """Initiates a backup of the current running configuration of the connected switch."""
        if self.connection:
            filename = self.config_manager.backup_config(self.connection, self.ip)
            if filename:
                self.output_area.append(f'Backup completed: {filename}')
                QMessageBox.information(self, "Backup", f"Configuration saved to '{filename}'.")
            else:
                self.output_area.append('Backup error!')
                QMessageBox.critical(self, "Error", "Error backing up configuration!")
        else:
            self.output_area.append("Please connect to a switch first!")

    def open_global_config_dialog(self):
        """Opens the global configuration dialog."""
        if self.connection:
            global_dialog = GlobalConfigDialog(self.connection, self)
            global_dialog.exec_()
        else:
            QMessageBox.warning(self, "Warning", "Please connect to a switch first!")

    def open_bulk_interface_config(self):
        """
        Opens a dialog to apply configuration to selected interfaces.
        """
        selected_interfaces = []
        for i in range(self.interface_list.count()):
            item = self.interface_list.item(i)
            custom_widget = self.interface_list.itemWidget(item)
            if custom_widget and custom_widget.is_checked():
                selected_interfaces.append(custom_widget.get_interface_name())

        if not selected_interfaces:
            QMessageBox.warning(self, "Warning", "Please select at least one interface.")
            return

        if self.connection:
            bulk_dialog = BulkInterfaceConfigDialog(self.connection, selected_interfaces, self)
            bulk_dialog.exec_()
        else:
            QMessageBox.warning(self, "Warning", "Please connect to a switch first!")

    def update_bulk_apply_button(self):
        """Enables/disables the bulk apply button based on interface selection."""
        has_selection = False
        for i in range(self.interface_list.count()):
            item = self.interface_list.item(i)
            custom_widget = self.interface_list.itemWidget(item)
            if custom_widget and custom_widget.is_checked():
                has_selection = True
                break
        self.bulk_apply_button.setEnabled(has_selection)

    def toggle_gigabit_selection(self, state):
        """
        Toggles the selection of all GigabitEthernet interfaces based on checkbox state.
        """
        is_checked = (state == Qt.Checked)
        for i in range(self.interface_list.count()):
            item = self.interface_list.item(i)
            custom_widget = self.interface_list.itemWidget(item)
            if custom_widget:
                interface_name = custom_widget.get_interface_name()
                if "GigabitEthernet" in interface_name or "Gi" in interface_name:
                    custom_widget.set_checked(is_checked)
        
        # Update bulk apply button state
        self.update_bulk_apply_button()

    def load_interfaces(self):
        """Loads and displays the list of interfaces from the switch."""
        print("DEBUG: Starting load_interfaces...")
        if self.connection:
            try:
                print("DEBUG: Sending 'show ip interface brief' command...")
                output = self.connection.send_command("show ip interface brief")
                print("DEBUG: 'show ip interface brief' command successful.")
                self.interface_list.clear()
                lines = output.split('\n')
                data_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith("Interface")]

                for line in data_lines:
                    columns = line.split()
                    if len(columns) >= 6:
                        interface_name = columns[0]
                        status = "unknown" 
                        if "up" in line.lower() and "down" not in line.lower():
                            status = "up"
                        elif "down" in line.lower() and "administratively" not in line.lower():
                            status = "down"
                        elif "administratively down" in line.lower():
                            status = "administratively down"
                        
                        try:
                            status_icon = self.create_interface_icon(status)
                        except Exception as e:
                            print(f"DEBUG: Error creating interface icon for {interface_name}: {str(e)}")
                            status_icon = QIcon() # Fallback to empty icon on error

                        list_item = QListWidgetItem(self.interface_list)
                        custom_widget = InterfaceListItemWidget(interface_name, status_icon)
                        
                        list_item.setSizeHint(custom_widget.sizeHint())
                        self.interface_list.setItemWidget(list_item, custom_widget)
                print("DEBUG: load_interfaces completed successfully.")
            except Exception as e:
                print(f"DEBUG: Error in load_interfaces: {str(e)}")
                self.output_area.append(f'Error loading interfaces: {str(e)}')
        else:
            print("DEBUG: Not connected to switch in load_interfaces, clearing list.")
            self.interface_list.clear()

    def create_interface_icon(self, status):
        """Creates and returns a QIcon based on the interface status."""
        icon_path = ""
        if "up" in status.lower() and "down" not in status.lower():
            icon_path = "green_icon.png"
        elif "down" in status.lower() and "administratively" not in status.lower():
            icon_path = "red_icon.png"
        elif "administratively down" in status.lower():
            icon_path = "black_icon.png"
        
        if icon_path:
            full_icon_path = os.path.abspath(icon_path) 
            if os.path.exists(full_icon_path):
                return QIcon(full_icon_path)
        
        # Create a simple colored pixmap as fallback
        pixmap = QPixmap(16, 16)
        if "up" in status.lower() and "down" not in status.lower():
            pixmap.fill(Qt.green)
        elif "down" in status.lower() and "administratively" not in status.lower():
            pixmap.fill(Qt.red)
        elif "administratively down" in status.lower():
            pixmap.fill(Qt.black)
        else:
            pixmap.fill(Qt.gray)
        
        return QIcon(pixmap)

    def load_vlans(self):
        """Loads and displays the list of VLANs from the switch."""
        if self.connection:
            try:
                output = self.connection.send_command("show vlan brief")
                self.vlan_list.clear()
                lines = output.split('\n')
                for line in lines:
                    if line.strip() and line[0].isdigit():
                        columns = line.split()
                        if len(columns) >= 2:
                            vlan_id = columns[0]
                            vlan_name = columns[1]
                            self.vlan_list.addItem(f"VLAN {vlan_id}: {vlan_name}")
            except Exception as e:
                self.output_area.append(f'Error loading VLANs: {str(e)}')
        else:
            self.vlan_list.clear()

    def open_interface_config(self, item):
        """Opens the interface configuration dialog for the double-clicked interface."""
        custom_widget = self.interface_list.itemWidget(item)
        if custom_widget and self.connection:
            interface_name = custom_widget.get_interface_name()
            config_dialog = InterfaceConfigDialog(self.connection, interface_name, self)
            config_dialog.exec_()

    def show_interface_details(self, item):
        """Displays detailed configuration for the clicked interface."""
        custom_widget = self.interface_list.itemWidget(item)
        if custom_widget and self.connection:
            interface_name = custom_widget.get_interface_name()
            try:
                output = self.connection.send_command(f"show running-config interface {interface_name}")
                self.interface_info.setPlainText(output)
            except Exception as e:
                self.interface_info.setPlainText(f'Error: {str(e)}')

    def show_vlan_ports(self, item):
        """Displays ports associated with the selected VLAN."""
        if self.connection:
            vlan_text = item.text()
            vlan_id = vlan_text.split(':')[0].replace('VLAN ', '')
            try:
                output = self.connection.send_command(f"show vlan id {vlan_id}")
                self.interface_info.setPlainText(output)
            except Exception as e:
                self.interface_info.setPlainText(f'Error: {str(e)}')

    def execute_command(self):
        """Executes a single command entered by the user."""
        if self.connection:
            command = self.command_input.text().strip()
            if not command:
                return

            # Check if the command is a configuration command
            if command.lower().startswith("conf") or \
               command.lower().startswith("config") or \
               command.lower().startswith("configure terminal"):
                self.output_area.append(f'\n> {command}\nPlease use "Apply Global Config" button for configuration commands.')
                self.command_input.clear()
                return

            try:
                output = self.connection.send_command(command)
                self.output_area.append(f'\n> {command}\n{output}')
            except Exception as e:
                self.output_area.append(f'Error: {str(e)}')
            self.command_input.clear()
        else:
            self.output_area.append("Please connect to a switch first!")

    def on_search_interface_changed(self, state):
        """Handle Search Interface checkbox state change."""
        if state == Qt.Checked:
            self.inc_checkbox.setEnabled(True)
            self.exc_checkbox.setEnabled(True)
        else:
            self.inc_checkbox.setEnabled(False)
            self.exc_checkbox.setEnabled(False)
            self.inc_checkbox.setChecked(False)
            self.exc_checkbox.setChecked(False)

    def on_inc_checkbox_changed(self, state):
        """Handle inc checkbox state change."""
        if state == Qt.Checked:
            self.exc_checkbox.setChecked(False)
            self.open_search_dialog('include')

    def on_exc_checkbox_changed(self, state):
        """Handle exc checkbox state change."""
        if state == Qt.Checked:
            self.inc_checkbox.setChecked(False)
            self.open_search_dialog('exclude')

    def open_search_dialog(self, search_mode):
        """Open the interface search dialog."""
        if not self.connection:
            QMessageBox.warning(self, "Warning", "Please connect to a switch first.")
            if search_mode == 'include':
                self.inc_checkbox.setChecked(False)
            else:
                self.exc_checkbox.setChecked(False)
            return

        search_dialog = SearchDialog(self, self.connection, search_mode)
        search_dialog.interfaces_selected.connect(self.on_search_interfaces_selected)
        
        result = search_dialog.exec_()
        if result == QDialog.Rejected:
            if search_mode == 'include':
                self.inc_checkbox.setChecked(False)
            else:
                self.exc_checkbox.setChecked(False)

    def on_search_interfaces_selected(self, selected_interfaces):
        """Handle interfaces selected from search dialog."""
        if selected_interfaces:
            bulk_dialog = BulkInterfaceConfigDialog(self.connection, selected_interfaces, self)
            bulk_dialog.exec_()
        
        self.inc_checkbox.setChecked(False)
        self.exc_checkbox.setChecked(False)


# New SortableSwitchListWidget Class
class SortableSwitchListWidget(QListWidget):
    """
    A QListWidget subclass that enables drag and drop for reordering items.
    Emits a signal when the order changes.
    """
    order_changed = pyqtSignal(list) # Signal to emit the new order of IPs

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True) # Visual feedback for dropping

    def dropEvent(self, event):
        """Overrides the default drop event to capture the new order."""
        if event.source() == self and event.dropAction() == Qt.MoveAction:
            super().dropEvent(event)
            # After the internal move, get the new order of IPs
            new_order_ips = []
            for i in range(self.count()):
                item_text = self.item(i).text()
                # Extract IP from the item text (e.g., "192.168.1.1 (SwitchName)" -> "192.168.1.1")
                ip = item_text.split(' ')[0]
                new_order_ips.append(ip)
            
            self.order_changed.emit(new_order_ips) # Emit the signal with the new order
            event.accept()
        else:
            event.ignore()

# CiscoSwitchGUI Class - Main Application Window (Tab Manager)
class CiscoSwitchGUI(QWidget):
    """
    Main application window. Manages the switch list and QTabWidget.
    """
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.initUI()
        self.load_saved_switches()

    def initUI(self):
        self.setWindowTitle('Cisco Switch Management Interface')
        self.setGeometry(100, 100, 1200, 800)

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()

        # Switch list with drag and drop
        left_layout.addWidget(QLabel('Saved Switches (Drag-Drop to Reorder):'))
        self.switch_list = SortableSwitchListWidget()
        self.switch_list.itemClicked.connect(self.load_selected_switch_to_inputs)
        self.switch_list.itemDoubleClicked.connect(self.open_switch_tab)
        self.switch_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.switch_list.customContextMenuRequested.connect(self.show_switch_context_menu)
        # Connect the custom signal
        self.switch_list.order_changed.connect(self.save_switch_order_after_drag)
        left_layout.addWidget(self.switch_list)

        # New switch addition inputs
        add_switch_group = QVBoxLayout()
        add_switch_group.addWidget(QLabel('Add/Update Switch:'))
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IP Address")
        add_switch_group.addWidget(self.ip_input)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        add_switch_group.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        add_switch_group.addWidget(self.pass_input)

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_switch)
        add_switch_group.addWidget(self.save_button)
        
        left_layout.addLayout(add_switch_group)

        self.manage_templates_button = QPushButton("Manage Templates")
        self.manage_templates_button.clicked.connect(self.open_template_manager_dialog)
        left_layout.addWidget(self.manage_templates_button)

        main_layout.addLayout(left_layout, 1)

        # Tabbed Area (Right side)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        main_layout.addWidget(self.tab_widget, 3)

        self.setLayout(main_layout)

    def save_switch_order_after_drag(self, new_ordered_ips):
        """
        Receives the new order of switch IPs after a drag-and-drop operation
        and saves this new order to the configuration file.
        """
        print(f"DEBUG: New switch order received: {new_ordered_ips}")
        self.config_manager.save_switches_order(new_ordered_ips)

    def open_template_manager_dialog(self):
        """Opens the dialog for managing configuration templates."""
        template_dialog = TemplateManagerDialog(self)
        template_dialog.exec_()

    def show_switch_context_menu(self, position):
        """Displays a context menu for the switch list items."""
        selected_item = self.switch_list.itemAt(position)
        if selected_item:
            context_menu = QMenu(self)
            
            edit_action = QAction("Edit", self)
            edit_action.triggered.connect(self.edit_selected_switch)
            context_menu.addAction(edit_action)
            
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(self.delete_selected_switch)
            context_menu.addAction(delete_action)
            
            context_menu.exec_(self.switch_list.viewport().mapToGlobal(position))

    def edit_selected_switch(self):
        """Allows editing of selected switch's IP, username, password, and name."""
        current_item = self.switch_list.currentItem()
        if current_item:
            current_text = current_item.text()
            current_ip = current_text.split(' ')[0]
            
            # Get current credentials
            username, password = self.config_manager.get_switch_credentials(current_ip)
            
            # Get current name from the display text
            current_name = ""
            if ' (' in current_text and ')' in current_text:
                current_name = current_text.split(' (')[1].rstrip(')')
            
            # Create edit dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Switch")
            dialog.setModal(True)
            dialog.resize(300, 200)
            
            layout = QVBoxLayout()
            
            layout.addWidget(QLabel("IP Address:"))
            ip_edit = QLineEdit(current_ip)
            layout.addWidget(ip_edit)
            
            layout.addWidget(QLabel("Switch Name (Optional):"))
            name_edit = QLineEdit(current_name)
            layout.addWidget(name_edit)
            
            layout.addWidget(QLabel("Username:"))
            user_edit = QLineEdit(username or "")
            layout.addWidget(user_edit)
            
            layout.addWidget(QLabel("Password:"))
            pass_edit = QLineEdit(password or "")
            pass_edit.setEchoMode(QLineEdit.Password)
            layout.addWidget(pass_edit)
            
            button_layout = QHBoxLayout()
            save_button = QPushButton("Save")
            cancel_button = QPushButton("Cancel")
            button_layout.addWidget(save_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            save_button.clicked.connect(dialog.accept)
            cancel_button.clicked.connect(dialog.reject)
            
            if dialog.exec_() == QDialog.Accepted:
                new_ip = ip_edit.text().strip()
                new_name = name_edit.text().strip()
                new_username = user_edit.text().strip()
                new_password = pass_edit.text().strip()
                
                if new_ip and new_username and new_password:
                    # If IP changed, delete old entry
                    if new_ip != current_ip:
                        self.config_manager.delete_switch(current_ip)
                    
                    # Save new/updated entry
                    if self.config_manager.save_switch_credentials(new_ip, new_username, new_password, new_name):
                        QMessageBox.information(self, "Success", "Switch information updated!")
                        self.load_saved_switches()
                    else:
                        QMessageBox.critical(self, "Error", "Error updating switch information!")
                else:
                    QMessageBox.warning(self, "Warning", "IP, username and password fields cannot be empty!")

    def delete_selected_switch(self):
        """Deletes the selected switch from the list and keyring."""
        current_item = self.switch_list.currentItem()
        if current_item:
            ip = current_item.text().split(' ')[0]
            reply = QMessageBox.question(self, 'Delete Confirmation', f'Are you sure you want to delete switch at {ip}?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.config_manager.delete_switch(ip):
                    QMessageBox.information(self, "Success", "Switch deleted!")
                    self.load_saved_switches()
                else:
                    QMessageBox.critical(self, "Error", "Error deleting switch!")

    def load_saved_switches(self):
        """Loads saved switches (including IP and Name) into the list widget."""
        self.switch_list.clear()
        switches_data = self.config_manager.get_saved_switches_full()
        for switch_info in switches_data:
            ip = switch_info["ip"]
            name = switch_info.get("name", "")
            
            # Display format: "IP (Name)" or just "IP" if no name
            display_text = f"{ip} ({name})" if name else ip
            self.switch_list.addItem(display_text)

    def save_switch(self):
        """Saves a new switch's IP, username, and password."""
        ip = self.ip_input.text().strip()
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        
        if ip and username and password:
            # Prompt for optional switch name
            name, ok = QInputDialog.getText(self, "Switch Name", "Enter a name for the switch (optional):")
            if not ok:
                name = ""  # User cancelled, use empty name
            
            if self.config_manager.save_switch_credentials(ip, username, password, name.strip()):
                QMessageBox.information(self, "Success", "Switch saved!")
                self.load_saved_switches()
                self.ip_input.clear()
                self.user_input.clear()
                self.pass_input.clear()
            else:
                QMessageBox.critical(self, "Error", "Failed to save switch!")
        else:
            QMessageBox.warning(self, "Warning", "Please fill in IP, username and password fields!")

    def load_selected_switch_to_inputs(self, item):
        """Fills IP, username, and password inputs only. Does not open a tab."""
        ip = item.text().split(' ')[0]
        username, password = self.config_manager.get_switch_credentials(ip)
        
        if username and password:
            self.ip_input.setText(ip)
            self.user_input.setText(username)
            self.pass_input.setText(password)

    def open_switch_tab(self, item):
        """Opens a new tab for the selected saved switch when double-clicked."""
        ip = item.text().split(' ')[0]
        username, password = self.config_manager.get_switch_credentials(ip)
        
        if username and password:
            # Check if tab already exists
            for i in range(self.tab_widget.count()):
                tab_widget = self.tab_widget.widget(i)
                if hasattr(tab_widget, 'ip') and tab_widget.ip == ip:
                    self.tab_widget.setCurrentIndex(i)
                    QMessageBox.information(self, "Info", f"Tab for {ip} is already open!")
                    return

            # Create new tab
            tab = SwitchTabWidget(ip, username, password)
            tab_name = f"{ip}"
            self.tab_widget.addTab(tab, tab_name)
            self.tab_widget.setCurrentWidget(tab)
        else:
            QMessageBox.critical(self, "Error", f"Credentials not found for {ip}!")

    def close_tab(self, index):
        """Triggered when a tab close request is received."""
        tab_widget = self.tab_widget.widget(index)
        if hasattr(tab_widget, 'disconnect_from_switch'):
            tab_widget.disconnect_from_switch()
        self.tab_widget.removeTab(index)


if __name__ == '__main__':
    app = QApplication([])
    
    # Create icon files if they don't exist
    icon_files = ['green_icon.png', 'red_icon.png', 'black_icon.png']
    for icon_file in icon_files:
        if not os.path.exists(icon_file):
            pixmap = QPixmap(16, 16)
            if 'green' in icon_file:
                pixmap.fill(Qt.green)
            elif 'red' in icon_file:
                pixmap.fill(Qt.red)
            elif 'black' in icon_file:
                pixmap.fill(Qt.black)
            pixmap.save(icon_file)
    
    window = CiscoSwitchGUI()
    window.show()
    app.exec_()