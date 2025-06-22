import sys
import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QLabel, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QGridLayout, QDoubleSpinBox, QSpinBox,
    QFileDialog, QStatusBar, QSizePolicy
)
from PyQt5.QtCore import Qt
from fem_analysis import FEMPlateModalAnalysis
from visualization import ModeShapeCanvas

class FEMInputPanel(QGroupBox):
    """Input panel for FEM parameters with validation"""
    
    def __init__(self, parent=None):
        super().__init__("Input Parameters", parent)
        self.layout = QGridLayout()
        self.setMinimumWidth(400)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        # Geometry
        self.layout.addWidget(QLabel("Length (m):"), 0, 0)
        self.length_input = QDoubleSpinBox()
        self.length_input.setRange(0.1, 10.0)
        self.length_input.setValue(1.0)
        self.length_input.setSingleStep(0.1)
        self.layout.addWidget(self.length_input, 0, 1)
        
        self.layout.addWidget(QLabel("Width (m):"), 0, 2)
        self.width_input = QDoubleSpinBox()
        self.width_input.setRange(0.1, 10.0)
        self.width_input.setValue(1.0)
        self.width_input.setSingleStep(0.1)
        self.layout.addWidget(self.width_input, 0, 3)
        
        # Mesh
        self.layout.addWidget(QLabel("Elements X:"), 1, 0)
        self.nx_input = QSpinBox()
        self.nx_input.setRange(2, 100)
        self.nx_input.setValue(10)
        self.layout.addWidget(self.nx_input, 1, 1)
        
        self.layout.addWidget(QLabel("Elements Y:"), 1, 2)
        self.ny_input = QSpinBox()
        self.ny_input.setRange(2, 100)
        self.ny_input.setValue(10)
        self.layout.addWidget(self.ny_input, 1, 3)
        
        # Material
        self.layout.addWidget(QLabel("Young's Modulus (Pa):"), 2, 0)
        self.E_input = QDoubleSpinBox()
        self.E_input.setRange(1e6, 1e12)
        self.E_input.setValue(2.1e11)
        self.E_input.setSingleStep(1e9)
        self.layout.addWidget(self.E_input, 2, 1)
        
        self.layout.addWidget(QLabel("Poisson's Ratio:"), 2, 2)
        self.nu_input = QDoubleSpinBox()
        self.nu_input.setRange(0.0, 0.5)
        self.nu_input.setValue(0.3)
        self.nu_input.setSingleStep(0.05)
        self.layout.addWidget(self.nu_input, 2, 3)
        
        self.layout.addWidget(QLabel("Density (kg/m³):"), 3, 0)
        self.rho_input = QDoubleSpinBox()
        self.rho_input.setRange(1, 20000)
        self.rho_input.setValue(7800)
        self.rho_input.setSingleStep(100)
        self.layout.addWidget(self.rho_input, 3, 1)
        
        self.layout.addWidget(QLabel("Thickness (m):"), 3, 2)
        self.thickness_input = QDoubleSpinBox()
        self.thickness_input.setRange(0.001, 0.5)
        self.thickness_input.setValue(0.01)
        self.thickness_input.setSingleStep(0.001)
        self.layout.addWidget(self.thickness_input, 3, 3)
        
        # Boundary Conditions
        self.layout.addWidget(QLabel("Fixed Edges:"), 4, 0)
        self.bc_edges = QComboBox()
        self.bc_edges.setEditable(False)
        self.bc_edges.addItems(["Left", "Right", "Top", "Bottom"])
        self.bc_edges.setMinimumWidth(100)
        self.layout.addWidget(self.bc_edges, 4, 1)
        
        self.add_edge_btn = QPushButton("Add Edge")
        self.add_edge_btn.clicked.connect(self.add_edge)
        self.layout.addWidget(self.add_edge_btn, 4, 2)
        
        self.clear_edges_btn = QPushButton("Clear Edges")
        self.clear_edges_btn.clicked.connect(self.clear_edges)
        self.layout.addWidget(self.clear_edges_btn, 4, 3)
        
        self.bc_display = QLabel("Selected: None")
        self.bc_display.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.layout.addWidget(QLabel("Selected Edges:"), 5, 0)
        self.layout.addWidget(self.bc_display, 5, 1, 1, 3)
        
        # Number of modes
        self.layout.addWidget(QLabel("Number of Modes:"), 6, 0)
        self.num_modes_input = QSpinBox()
        self.num_modes_input.setRange(1, 20)
        self.num_modes_input.setValue(5)
        self.layout.addWidget(self.num_modes_input, 6, 1)
        
        self.setLayout(self.layout)
        self.bc_edges_list = []
        
    def add_edge(self):
        edge = self.bc_edges.currentText().lower()
        if edge not in self.bc_edges_list:
            self.bc_edges_list.append(edge)
            self.update_bc_display()
    
    def clear_edges(self):
        self.bc_edges_list = []
        self.update_bc_display()
        
    def update_bc_display(self):
        if self.bc_edges_list:
            self.bc_display.setText(", ".join(self.bc_edges_list))
        else:
            self.bc_display.setText("None")
    
    def get_parameters(self):
        return {
            'length': self.length_input.value(),
            'width': self.width_input.value(),
            'nx': self.nx_input.value(),
            'ny': self.ny_input.value(),
            'E': self.E_input.value(),
            'nu': self.nu_input.value(),
            'rho': self.rho_input.value(),
            'thickness': self.thickness_input.value(),
            'fixed_edges': self.bc_edges_list,
            'num_modes': self.num_modes_input.value()
        }
    
    def validate_inputs(self):
        """Validate inputs and return error message if any"""
        if not self.bc_edges_list:
            return "Please select at least one clamped edge"
        
        if self.nx_input.value() < 2 or self.ny_input.value() < 2:
            return "Mesh must have at least 2 elements in each direction"
            
        if self.thickness_input.value() <= 0:
            return "Thickness must be positive"
            
        return None


class ResultsTable(QTableWidget):
    """Table for displaying natural frequencies with sorting"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Mode", "Frequency (Hz)"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)
        self.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 4px;
            }
        """)
        
    def update_data(self, frequencies):
        self.setRowCount(len(frequencies))
        for i, freq in enumerate(frequencies):
            self.setItem(i, 0, QTableWidgetItem(f"{i+1}"))
            freq_item = QTableWidgetItem(f"{freq:.2f}")
            freq_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.setItem(i, 1, freq_item)


class MainWindow(QMainWindow):
    """Main application window with status bar and save functionality"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2D Plate Modal Analyzer")
        self.setGeometry(100, 100, 1400, 800)
        
        # Central widget and layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Left panel (inputs)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        self.input_panel = FEMInputPanel()
        left_panel.addWidget(self.input_panel)
        
        # Run button
        self.run_btn = QPushButton("Run Modal Analysis")
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                height: 35px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        self.run_btn.clicked.connect(self.run_analysis)
        left_panel.addWidget(self.run_btn)
        
        # Results table
        left_panel.addWidget(QLabel("Natural Frequencies:", styleSheet="font-weight: bold;"))
        self.results_table = ResultsTable()
        self.results_table.setMaximumHeight(250)
        left_panel.addWidget(self.results_table)
        
        # Save button
        self.save_btn = QPushButton("Save Results")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                height: 35px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        self.save_btn.clicked.connect(self.save_results)
        self.save_btn.setEnabled(False)
        left_panel.addWidget(self.save_btn)
        
        # Right panel (visualization)
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        
        # Mode visualization
        vis_group = QGroupBox("Mode Shape Visualization")
        vis_layout = QVBoxLayout(vis_group)
        self.mode_canvas = ModeShapeCanvas(self)
        vis_layout.addWidget(self.mode_canvas)
        right_panel.addWidget(vis_group)
        
        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Select Mode:", styleSheet="font-weight: bold;"))
        self.mode_combo = QComboBox()
        self.mode_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                min-width: 200px;
            }
        """)
        self.mode_combo.currentIndexChanged.connect(self.display_mode_shape)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        right_panel.addLayout(mode_layout)
        
        # Combine panels
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)
        
        self.setCentralWidget(central_widget)
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to analyze")
        
        # Analysis results storage
        self.nodes = None
        self.elements = None
        self.mode_shapes = None
        self.frequencies = None
        
    def run_analysis(self):
        """Run FEM analysis and display results"""
        # Validate inputs
        error = self.input_panel.validate_inputs()
        if error:
            QMessageBox.warning(self, "Input Error", error)
            return
            
        try:
            self.status_bar.showMessage("Running modal analysis...")
            QApplication.processEvents()  # Update UI
            
            params = self.input_panel.get_parameters()
            
            # Create and run analysis
            fem = FEMPlateModalAnalysis(
                length=params['length'],
                width=params['width'],
                nx=params['nx'],
                ny=params['ny'],
                E=params['E'],
                nu=params['nu'],
                rho=params['rho'],
                thickness=params['thickness']
            )
            
            self.frequencies, self.mode_shapes = fem.solve_modes(
                num_modes=params['num_modes'],
                fixed_edges=params['fixed_edges']
            )
            
            # Store results
            self.nodes = fem.nodes
            
            # Update UI
            self.results_table.update_data(self.frequencies)
            self.mode_combo.clear()
            self.mode_combo.addItems([f"Mode {i+1} ({freq:.2f} Hz)" 
                                    for i, freq in enumerate(self.frequencies)])
            
            # Display first mode
            if self.mode_shapes is not None:
                self.display_mode_shape(0)
                
            self.save_btn.setEnabled(True)
            self.status_bar.showMessage(f"Analysis completed: {len(self.frequencies)} modes found")
                
        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", f"Error during analysis:\n{str(e)}")
            self.status_bar.showMessage("Analysis failed")
            
    def display_mode_shape(self, index):
        """Display selected mode shape"""
        if self.mode_shapes is not None and 0 <= index < self.mode_shapes.shape[1]:
            self.mode_canvas.plot_mode_shape(
                self.nodes,
                self.mode_shapes[:, index],
                title=f"Mode {index+1} Shape"
            )
            
    def save_results(self):
        """Save analysis results to file"""
        if self.frequencies is None:
            return
            
        options = QFileDialog.Options()
        file_name, selected_filter = QFileDialog.getSaveFileName(
            self, "Save Results", "modal_analysis_results", 
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)", 
            options=options
        )
        
        if not file_name:
            return
            
        try:
            # Add extension if not provided
            if selected_filter == "Text Files (*.txt)" and not file_name.endswith('.txt'):
                file_name += '.txt'
            elif selected_filter == "CSV Files (*.csv)" and not file_name.endswith('.csv'):
                file_name += '.csv'
                
            with open(file_name, 'w') as f:
                # Write header with parameters
                params = self.input_panel.get_parameters()
                f.write("2D Plate Modal Analysis Results\n")
                f.write("=" * 60 + "\n")
                f.write(f"Plate Dimensions: {params['length']}m x {params['width']}m\n")
                f.write(f"Thickness: {params['thickness']}m\n")
                f.write(f"Material Properties:\n")
                f.write(f"  Young's Modulus: {params['E']:.2e} Pa\n")
                f.write(f"  Poisson's Ratio: {params['nu']}\n")
                f.write(f"  Density: {params['rho']} kg/m³\n")
                f.write(f"Mesh: {params['nx']}x{params['ny']} elements\n")
                f.write(f"Boundary Conditions: {', '.join(params['fixed_edges']) or 'None'}\n")
                f.write("=" * 60 + "\n\n")
                
                # Write frequencies
                f.write("Natural Frequencies (Hz):\n")
                f.write("Mode\tFrequency\n")
                f.write("-" * 30 + "\n")
                for i, freq in enumerate(self.frequencies):
                    f.write(f"{i+1}\t{freq:.4f}\n")
                
                # Write mode shapes
                f.write("\n\nMode Shapes (Normalized Displacements):\n")
                for mode_idx in range(len(self.frequencies)):
                    f.write(f"\nMode {mode_idx+1} (Frequency: {self.frequencies[mode_idx]:.2f} Hz):\n")
                    for i in range(self.nodes.shape[0]):
                        x, y = self.nodes[i]
                        disp = self.mode_shapes[i, mode_idx]
                        f.write(f"  Node {i+1}: ({x:.4f}, {y:.4f})\tDisplacement: {disp:.6f}\n")
            
            self.status_bar.showMessage(f"Results saved to {file_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save results:\n{str(e)}")
            self.status_bar.showMessage("Save failed")