class ExpiryDialog(QDialog):
    """Simple dialog to show expiring items"""
    
    def __init__(self, parent, logger, expiring_items):
        super().__init__(parent)
        self.logger = logger
        self.expiring_items = expiring_items
        self.setWindowTitle("Expiring Food Alert")
        self.setMinimumWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("Food Items Expiring Soon!")
        title_label.setStyleSheet("font-weight: bold; color: red;")
        layout.addWidget(title_label)
        
        items_text = ""
        for name, days_left in self.expiring_items:
            if days_left == 0:
                items_text += f"• {name} - EXPIRES TODAY!\n"
            else:
                items_text += f"• {name} - Expires in {days_left} day(s)\n"
                
        items_label = QLabel(items_text)
        layout.addWidget(items_label)

        btn_layout = QHBoxLayout()
        
        suggest_btn = QPushButton("Suggest Recipes")
        suggest_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        suggest_btn.clicked.connect(self.suggest_recipes)
        btn_layout.addWidget(suggest_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def suggest_recipes(self):
        self.logger.suggest_recipes([name for name, _ in self.expiring_items])
        self.accept()

class StartupExpiryDialog(QDialog):
    """Dialog to show expiring items on startup with warning styling"""
    
    def __init__(self, parent, logger, expiring_items):
        super().__init__(parent)
        self.logger = logger
        self.expiring_items = expiring_items
        self.setWindowTitle("⚠️ Food Expiry Alert ⚠️")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout()
        
        # Create a frame with red background for the alert
        alert_frame = QFrame()
        alert_frame.setStyleSheet("background-color: #FFCCCC; border-radius: 5px; padding: 10px;")
        alert_layout = QVBoxLayout(alert_frame)
        
        # Add warning icon and title
        title_layout = QHBoxLayout()
        warning_label = QLabel("⚠️")
        warning_label.setStyleSheet("font-size: 24px;")
        title_layout.addWidget(warning_label)
        
        title_label = QLabel("Food Items Expiring Soon!")
        title_label.setStyleSheet("font-weight: bold; color: #CC0000; font-size: 16px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        warning_label2 = QLabel("⚠️")
        warning_label2.setStyleSheet("font-size: 24px;")
        title_layout.addWidget(warning_label2)
        
        alert_layout.addLayout(title_layout)
        
        # Add horizontal separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #CC0000;")
        alert_layout.addWidget(separator)
        
        # Add expiring items list
        items_text = ""
        for name, days_left in self.expiring_items:
            if days_left == 0:
                items_text += f"• <b>{name}</b> - <span style='color: #CC0000;'>EXPIRES TODAY!</span><br>"
            elif days_left == 1:
                items_text += f"• <b>{name}</b> - <span style='color: #FF6600;'>Expires TOMORROW!</span><br>"
            else:
                items_text += f"• <b>{name}</b> - Expires in {days_left} days<br>"
                
        items_label = QLabel()
        items_label.setText(items_text)
        items_label.setStyleSheet("font-size: 14px;")
        items_label.setTextFormat(Qt.RichText)
        alert_layout.addWidget(items_label)
        
        # Add the alert frame to main layout
        layout.addWidget(alert_frame)
        
        # Add progress bar to show urgency
        urgency_label = QLabel("Food waste risk level:")
        urgency_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(urgency_label)
        
        urgency_bar = QProgressBar()
        urgency_bar.setRange(0, 100)
        
        # Calculate urgency based on expiry dates
        total_items = len(self.expiring_items)
        expiring_today = sum(1 for _, days in self.expiring_items if days == 0)
        expiring_tomorrow = sum(1 for _, days in self.expiring_items if days == 1)
        
        urgency_value = min(100, int((expiring_today * 50 + expiring_tomorrow * 30 + (total_items - expiring_today - expiring_tomorrow) * 10) / total_items))
        urgency_bar.setValue(urgency_value)
        
        # Set color based on urgency
        if urgency_value > 70:
            urgency_bar.setStyleSheet("QProgressBar::chunk { background-color: #CC0000; }")
        elif urgency_value > 40:
            urgency_bar.setStyleSheet("QProgressBar::chunk { background-color: #FF6600; }")
        else:
            urgency_bar.setStyleSheet("QProgressBar::chunk { background-color: #FFCC00; }")
            
        layout.addWidget(urgency_bar)

        # Add buttons
        btn_layout = QHBoxLayout()
        
        suggest_btn = QPushButton("Suggest Recipes")
        suggest_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        suggest_btn.clicked.connect(self.suggest_recipes)
        btn_layout.addWidget(suggest_btn)
        
        close_btn = QPushButton("Dismiss")
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # Tips for preventing food waste
        tips_frame = QFrame()
        tips_frame.setStyleSheet("background-color: #E8F5E9; border-radius: 5px; padding: 8px;")
        tips_layout = QVBoxLayout(tips_frame)
        
        tips_label = QLabel("💡 <b>Tip:</b> Check your expiring items daily and plan meals accordingly to reduce food waste.")
        tips_label.setWordWrap(True)
        tips_layout.addWidget(tips_label)
        
        layout.addWidget(tips_frame)
        
        self.setLayout(layout)
    
    def suggest_recipes(self):
        self.logger.suggest_recipes([name for name, _ in self.expiring_items])
        self.accept()

class RecipeDialog(QDialog):
    """Dialog to display recipe suggestions"""
    
    def __init__(self, parent, recipe):
        super().__init__(parent)
        self.recipe = recipe
        self.setWindowTitle("Recipe Suggestion")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        name_label = QLabel(self.recipe["name"])
        name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(name_label)
        
        ingredients_label = QLabel("Ingredients:")
        ingredients_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(ingredients_label)
        
        ingredients_text = "• " + "\n• ".join(self.recipe["ingredients"])
        ingredients_list = QLabel(ingredients_text)
        layout.addWidget(ingredients_list)
        
        instructions_label = QLabel("Instructions:")
        instructions_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(instructions_label)
        
        instructions_text = QLabel(self.recipe["instructions"])
        instructions_text.setWordWrap(True)
        layout.addWidget(instructions_text)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

class RecipeSelectionDialog(QDialog):
    """Dialog to display multiple recipe options"""
    
    def __init__(self, parent, matching_recipes):
        super().__init__(parent)
        self.matching_recipes = matching_recipes
        self.selected_recipe = None
        self.setWindowTitle("Recipe Suggestions")
        self.setMinimumWidth(500)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("Suggested Recipes")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title_label)
        
        self.recipe_table = QTableWidget()
        self.recipe_table.setColumnCount(3)
        self.recipe_table.setHorizontalHeaderLabels(["Recipe Name", "Match %", "Matching Ingredients"])
        self.recipe_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recipe_table.setSelectionMode(QTableWidget.SingleSelection)
        self.recipe_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recipe_table.setAlternatingRowColors(True)
        
        self.recipe_table.setRowCount(len(self.matching_recipes))
        for row, match_data in enumerate(self.matching_recipes):
            recipe = match_data['recipe']
            self.recipe_table.setItem(row, 0, QTableWidgetItem(recipe['name']))
            self.recipe_table.setItem(row, 1, QTableWidgetItem(f"{int(match_data['match_percentage'])}%"))
            self.recipe_table.setItem(row, 2, QTableWidgetItem(", ".join(match_data['matched_ingredients'])))
        
        self.recipe_table.resizeColumnsToContents()
        layout.addWidget(self.recipe_table)
        
        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        view_btn = QPushButton("View Recipe")
        view_btn.setDefault(True)
        view_btn.clicked.connect(self.view_selected_recipe)
        btn_layout.addWidget(view_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def view_selected_recipe(self):
        selected_rows = self.recipe_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_recipe = self.matching_recipes[row]['recipe']
            self.accept()
        else:
            QMessageBox.information(self, "Selection Required", "Please select a recipe to view.") 