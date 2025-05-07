class FoodWasteLogger:
    """Simple Food Waste Logger to track groceries and prevent food waste"""
    
    def __init__(self):
        self.food_items = {}  # Dictionary to store all food items
        self.food_categories = {
            "Dairy": 7,      # Default shelf life in days
            "Meat": 4,
            "Vegetables": 7,
            "Fruits": 7,
            "Bakery": 5,
            "Pantry": 180
        }
        
        self.recipes = [
            {
                "name": "Vegetable Stir Fry",
                "ingredients": ["Carrot", "Broccoli", "Rice"],
                "instructions": "1. Chop vegetables into bite-sized pieces.\n2. Cook rice according to package instructions.\n3. Heat oil in a pan and stir fry vegetables for 5-7 minutes.\n4. Season with salt and pepper.\n5. Serve vegetables over rice."
            },
            {
                "name": "Chicken Salad",
                "ingredients": ["Chicken", "Tomato", "Spinach"],
                "instructions": "1. Cook chicken until no longer pink inside.\n2. Chop tomatoes and prepare spinach leaves.\n3. Combine all ingredients in a bowl.\n4. Add your favorite dressing and toss to coat."
            },
            {
                "name": "Fruit Smoothie",
                "ingredients": ["Banana", "Yogurt", "Milk"],
                "instructions": "1. Cut banana into chunks.\n2. Add banana, yogurt and milk to a blender.\n3. Blend until smooth.\n4. Pour into a glass and enjoy immediately."
            },
            {
                "name": "Simple Pasta",
                "ingredients": ["Pasta", "Tomato", "Cheese"],
                "instructions": "1. Cook pasta according to package instructions.\n2. While pasta cooks, dice tomatoes.\n3. Drain pasta and return to pot.\n4. Add tomatoes and grated cheese, stir until cheese melts."
            },
            {
                "name": "Quick Omelet",
                "ingredients": ["Eggs", "Cheese", "Spinach"],
                "instructions": "1. Beat eggs in a bowl.\n2. Heat butter in a pan over medium heat.\n3. Pour in eggs and cook until almost set.\n4. Add cheese and spinach to one half, fold over the other half.\n5. Cook until cheese melts."
            }
        ]
        
        self.setup_data_storage()
        self.load_data()
        self.setup_gui()
    
    def setup_data_storage(self):
        """Setup appropriate directories for data storage"""
        home_dir = Path.home()
        
        self.app_dir = home_dir / "FoodWasteLogger"
        try:
            self.app_dir.mkdir(exist_ok=True)
        except Exception as e:
            print(f"Could not create directory in home folder: {e}")
            self.app_dir = Path.cwd()
        
        self.data_file = self.app_dir / "food_inventory.json"
        print(f"Data will be stored at: {self.data_file}")
        
    def load_data(self):
        """Load existing food inventory data from file with improved error handling"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as file:
                    data = json.load(file)
                    for item_id, item_data in data.items():
                        if 'purchase_date' in item_data:
                            try:
                                item_data['purchase_date'] = datetime.strptime(
                                    item_data['purchase_date'], '%Y-%m-%d').date()
                            except ValueError:
                                item_data['purchase_date'] = datetime.now().date()
                                
                        if 'expiry_date' in item_data:
                            try:
                                item_data['expiry_date'] = datetime.strptime(
                                    item_data['expiry_date'], '%Y-%m-%d').date()
                            except ValueError:
                                item_data['expiry_date'] = datetime.now().date() + timedelta(days=7)
                    
                    self.food_items = data
        except Exception as e:
            print(f"Error loading data: {e}")
            QMessageBox.warning(None, "Data Loading Error", 
                              f"Could not load existing data: {e}\nStarting with an empty inventory.")
            self.food_items = {}
            
    def save_data(self):
        """Save current food inventory to file with improved error handling"""
        try:
            data_to_save = {}
            for item_id, item_data in self.food_items.items():
                data_to_save[item_id] = item_data.copy()
                if 'purchase_date' in data_to_save[item_id]:
                    data_to_save[item_id]['purchase_date'] = data_to_save[item_id]['purchase_date'].strftime('%Y-%m-%d')
                if 'expiry_date' in data_to_save[item_id]:
                    data_to_save[item_id]['expiry_date'] = data_to_save[item_id]['expiry_date'].strftime('%Y-%m-%d')
            
            if self.data_file.exists():
                backup_file = self.app_dir / "food_inventory_backup.json"
                try:
                    with open(self.data_file, 'r') as src, open(backup_file, 'w') as dst:
                        dst.write(src.read())
                except Exception as e:
                    print(f"Warning: Could not create backup: {e}")
            
            with open(self.data_file, 'w') as file:
                json.dump(data_to_save, file, indent=2)
                
        except Exception as e:
            error_msg = f"Could not save data: {e}"
            print(error_msg)
            QMessageBox.critical(self.window, "Save Error", error_msg)

    def add_food_item(self, name, category, quantity, purchase_date=None, expiry_date=None):
        """Add a new food item to the inventory"""
        if not purchase_date:
            purchase_date = datetime.now().date()
            
        if not expiry_date:
            shelf_life = self.food_categories.get(category, 7)
            expiry_date = purchase_date + timedelta(days=shelf_life)
        
        item_id = f"{name.lower().replace(' ', '')}{int(datetime.now().timestamp())}"
        
        self.food_items[item_id] = {
            "name": name,
            "category": category,
            "quantity": quantity,
            "purchase_date": purchase_date,
            "expiry_date": expiry_date
        }
        
        self.save_data()
        self.update_food_list()
        return item_id
        
    def remove_food_item(self, item_id):
        """Remove a food item from the inventory"""
        if item_id in self.food_items:
            del self.food_items[item_id]
            self.save_data()
            self.update_food_list()
            return True
        return False

    def show_recipe_selection_dialog(self, matching_recipes):
        """Show the recipe selection dialog"""
        selection_dialog = RecipeSelectionDialog(self.window, matching_recipes)
        result = selection_dialog.exec_()
    
        if result == QDialog.Accepted and selection_dialog.selected_recipe:
            recipe_dialog = RecipeDialog(self.window, selection_dialog.selected_recipe)
            recipe_dialog.exec_()
        
    def get_expiring_soon(self, days=3):
        """Get a list of items expiring within the specified number of days"""
        today = datetime.now().date()
        expiring_soon = []
        
        for item_id, item_data in self.food_items.items():
            days_left = (item_data['expiry_date'] - today).days
            if 0 <= days_left <= days:
                expiring_soon.append((item_data['name'], days_left))
                
        return expiring_soon
        
    def check_notifications(self):
        """Check for items that are about to expire and display notifications"""
        expiring_items = self.get_expiring_soon()
    
        if expiring_items:
            alert_dialog = ExpiryDialog(self.window, self, expiring_items)
            alert_dialog.exec_()
        else:
            QMessageBox.information(self.window, "Notification", "No items expiring soon!")

    def suggest_recipes(self, ingredient_list=None):
        """Suggest recipes based on available ingredients"""
        if ingredient_list is None:
            ingredient_list = [item['name'] for item in self.food_items.values()]
        
        print(f"Looking for recipes with ingredients: {ingredient_list}")
        
        matching_recipes = []
        
        for recipe in self.recipes:
            match_count = 0
            matched_ingredients = []
            
            for recipe_ing in recipe['ingredients']:
                for item in ingredient_list:
                    if (recipe_ing.lower() in item.lower() or 
                        item.lower() in recipe_ing.lower()):
                        match_count += 1
                        matched_ingredients.append(recipe_ing)
                        break
            
            if recipe['ingredients']:
                match_percentage = (match_count / len(recipe['ingredients'])) * 100
            else:
                match_percentage = 0
                
            if match_count > 0:
                matching_recipes.append({
                    'recipe': recipe,
                    'match_count': match_count,
                    'match_percentage': match_percentage,
                    'matched_ingredients': matched_ingredients
                })
        
        matching_recipes.sort(key=lambda x: x['match_count'], reverse=True)
        
        if matching_recipes:
            self.show_recipe_selection_dialog(matching_recipes)
        else:
            QMessageBox.information(self.window, "Recipe Suggestions", 
                            "No recipes found for your current inventory.")

    def update_expiry_date(self):
        """Update the expiry date based on the selected category"""
        category = self.category_dropdown.currentText()
        shelf_life = self.food_categories.get(category, 7)
        purchase_date = self.purchase_date_picker.date().toPyDate()
        expiry_date = purchase_date + timedelta(days=shelf_life)
        self.expiry_date_picker.setDate(QDate(expiry_date.year, expiry_date.month, expiry_date.day))

    # Custom sort to prioritize expiring soon (0-3 days), then expired, then good
    def sort_priority(self, days_left):
        if 0 <= days_left <= 3:
            return 0  # Expiring soon
        elif days_left < 0:
            return 1  # Expired
        else:
            return 2  # Good

    def update_food_list(self):
        """Update the displayed list of food items in the UI"""
        self.food_table.setRowCount(0)
        
        today = datetime.now().date()
    
        # Create a sorted list of items based on days_left (expired first)
        sorted_items = []
        for item_id, item_data in self.food_items.items():
            days_left = (item_data['expiry_date'] - today).days
            sorted_items.append((item_id, item_data, days_left))
    
        # Sort by days_left (expired items first)
        sorted_items.sort(key=lambda x: (self.sort_priority(x[2]), x[2]))

    
        row = 0
        for item_id, item_data, days_left in sorted_items:
            self.food_table.insertRow(row)
            self.food_table.setItem(row, 0, QTableWidgetItem(item_data['name']))
            self.food_table.setItem(row, 1, QTableWidgetItem(item_data['category']))
            self.food_table.setItem(row, 2, QTableWidgetItem(str(item_data['quantity'])))
            self.food_table.setItem(row, 3, QTableWidgetItem(item_data['purchase_date'].strftime('%Y-%m-%d')))
            self.food_table.setItem(row, 4, QTableWidgetItem(item_data['expiry_date'].strftime('%Y-%m-%d')))
            self.food_table.setItem(row, 5, QTableWidgetItem(f"{days_left} days"))
        
            color = QColor(200, 255, 200)  # Light green for non-expiring items
            if days_left < 0:
                color = QColor(255, 200, 200)  # Light red for expired
            elif days_left <= 3:
                color = QColor(255, 255, 200)  # Light yellow for expiring soon
                
            for col in range(self.food_table.columnCount()):
                self.food_table.item(row, col).setBackground(color)
            
            self.food_table.item(row, 0).setData(Qt.UserRole, item_id)
            row += 1

    def setup_gui(self):
        """Set up the graphical user interface"""
        self.app = QApplication([])
        self.window = QMainWindow()
        self.window.setWindowTitle("Food Waste Logger")
        self.window.resize(900, 600)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        top_frame = QWidget()
        top_layout = QGridLayout(top_frame)
        
        top_layout.addWidget(QLabel("Name:"), 0, 0)
        self.name_entry = QLineEdit()
        top_layout.addWidget(self.name_entry, 0, 1)
        
        top_layout.addWidget(QLabel("Category:"), 0, 2)
        self.category_dropdown = QComboBox()
        self.category_dropdown.addItems(list(self.food_categories.keys()))
        self.category_dropdown.currentTextChanged.connect(self.update_expiry_date)
        top_layout.addWidget(self.category_dropdown, 0, 3)
        
        top_layout.addWidget(QLabel("Quantity:"), 0, 4)
        self.quantity_entry = QLineEdit()
        top_layout.addWidget(self.quantity_entry, 0, 5)
        
        top_layout.addWidget(QLabel("Purchase Date:"), 1, 0)
        self.purchase_date_picker = QDateEdit()
        self.purchase_date_picker.setDate(QDate.currentDate())
        self.purchase_date_picker.setCalendarPopup(True)
        self.purchase_date_picker.dateChanged.connect(self.update_expiry_date)
        top_layout.addWidget(self.purchase_date_picker, 1, 1)
        
        top_layout.addWidget(QLabel("Expiry Date:"), 1, 2)
        self.expiry_date_picker = QDateEdit()
        default_expiry = datetime.now().date() + timedelta(days=7)
        self.expiry_date_picker.setDate(QDate(default_expiry.year, default_expiry.month, default_expiry.day))
        self.expiry_date_picker.setCalendarPopup(True)
        top_layout.addWidget(self.expiry_date_picker, 1, 3)
        
        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self.add_item_from_form)
        top_layout.addWidget(add_btn, 1, 5)
        
        main_layout.addWidget(top_frame)
        
        self.food_table = QTableWidget()
        self.food_table.setColumnCount(6)
        self.food_table.setHorizontalHeaderLabels(["Name", "Category", "Quantity", "Purchase Date", "Expiry Date", "Days Left"])
        self.food_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.food_table)
        
        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)
        
        scan_btn = QPushButton("Scan Product")
        scan_btn.setStyleSheet("background-color: #007BFF; color: white;")
        scan_btn.clicked.connect(self.scan_product)
        button_layout.addWidget(scan_btn)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        button_layout.addWidget(remove_btn)
        
        notify_btn = QPushButton("Check Expiring Items")
        notify_btn.clicked.connect(self.check_notifications)
        button_layout.addWidget(notify_btn)
        
        recipe_btn = QPushButton("Suggest Recipe")
        recipe_btn.clicked.connect(lambda: self.suggest_recipes())
        button_layout.addWidget(recipe_btn)

        weekly_report_btn = QPushButton("Weekly Report")
        weekly_report_btn.clicked.connect(lambda: self.generate_report("weekly"))
        button_layout.addWidget(weekly_report_btn)

        monthly_report_btn = QPushButton("Monthly Report")
        monthly_report_btn.clicked.connect(lambda: self.generate_report("monthly"))
        button_layout.addWidget(monthly_report_btn)
        
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.window.close)
        button_layout.addWidget(exit_btn)
        
        main_layout.addWidget(button_frame)
        
        self.window.setCentralWidget(main_widget)
        
        self.update_food_list()
        
        self.window.show()
    
    def scan_product(self):
        """Open the scan product dialog"""
        scan_dialog = ScanDialog(self.window, self)
        scan_dialog.exec_()
    
    def add_item_from_form(self):
        """Add a food item from the form inputs"""
        name = self.name_entry.text().strip()
        category = self.category_dropdown.currentText()
        
        try:
            quantity = float(self.quantity_entry.text())
        except ValueError:
            QMessageBox.critical(self.window, "Input Error", "Quantity must be a number.")
            return
            
        if not name:
            QMessageBox.critical(self.window, "Input Error", "Item name is required.")
            return
        
        purchase_date = self.purchase_date_picker.date().toPyDate()
        expiry_date = self.expiry_date_picker.date().toPyDate()
            
        self.add_food_item(name, category, quantity, purchase_date, expiry_date)
        
        self.name_entry.clear()
        self.quantity_entry.clear()
        
        QMessageBox.information(self.window, "Success", f"Added {name} to inventory.")
    
    def remove_selected(self):
        """Remove the selected item from the inventory"""
        selected_items = self.food_table.selectedItems()
        if not selected_items:
            QMessageBox.information(self.window, "Selection Required", "Please select an item to remove.")
            return
            
        selected_row = selected_items[0].row()
        name_item = self.food_table.item(selected_row, 0)
        item_id = name_item.data(Qt.UserRole)
        item_name = self.food_items[item_id]['name']
        
        reply = QMessageBox.question(self.window, "Confirm Removal", 
                                    f"Remove {item_name} from inventory?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.remove_food_item(item_id)

    def generate_report(self, report_type="weekly"):
        """Generate a report of food waste for the specified period"""
        today = datetime.now().date()
        
        if report_type == "weekly":
            start_date = today - timedelta(days=7)
            period_name = "Weekly"
        else:  # monthly
            start_date = today - timedelta(days=30)
            period_name = "Monthly"
        
        # Find items that were in the inventory during this period
        report_items = []
        total_items = 0
        expired_items = 0
        consumed_items = 0
        
        # Process current inventory items
        for item_id, item_data in self.food_items.items():
            if item_data['purchase_date'] >= start_date:
                total_items += 1
                days_left = (item_data['expiry_date'] - today).days
                
                status = "Active"
                if days_left < 0:
                    status = "Expired"
                    expired_items += 1
                
                report_items.append({
                    'name': item_data['name'],
                    'category': item_data['category'],
                    'status': status,
                    'purchase_date': item_data['purchase_date'].strftime('%Y-%m-%d'),
                    'expiry_date': item_data['expiry_date'].strftime('%Y-%m-%d')
                })
        
        # In a real application, we'd also check for items that were removed from inventory
        # during this period (e.g., consumed or discarded). For this demo, we'll simulate
        # some consumed items.
        
        # Simulate some consumed items (in a real app, this would come from tracking removals)
        if report_type == "weekly":
            consumed_items = random.randint(3, 8)  # Simulate 3-8 consumed items per week
        else:
            consumed_items = random.randint(12, 25)  # Simulate 12-25 consumed items per month
        
        # Calculate waste percentage
        if total_items + consumed_items > 0:
            waste_percentage = (expired_items / (total_items + consumed_items)) * 100
        else:
            waste_percentage = 0
        
        report_data = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': today.strftime('%Y-%m-%d'),
            'total_items': total_items + consumed_items,  # Total items in period
            'expired_items': expired_items,               # Items that expired
            'consumed_items': consumed_items,             # Items that were consumed
            'waste_percentage': waste_percentage,         # Percentage of waste
            'items': report_items                         # List of items in the report
        }
        
        # Show the report dialog
        report_dialog = ReportDialog(self.window, report_data, report_type)
        report_dialog.exec_()
    
    def run(self):
        """Run the application"""
        self.window.show()
    
        # Show expiring items notification on startup
        QTimer.singleShot(500, self.show_startup_notification)
    
        return self.app.exec_()

    def show_startup_notification(self):
        """Show notification about expiring products on startup"""
        try:
            expiring_items = self.get_expiring_soon()
            if expiring_items:
                startup_dialog = StartupExpiryDialog(self.window, self, expiring_items)
            startup_dialog.exec_()
        except Exception as e:
            print(f"Error in startup notification: {e}")
        # Don't let errors here crash the whole application
