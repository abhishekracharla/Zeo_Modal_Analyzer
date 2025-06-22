import numpy as np
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm

matplotlib.use('Qt5Agg')

class ModeShapeCanvas(FigureCanvas):
    """
    Matplotlib canvas for displaying mode shapes with consistent scaling
    
    Args:
        parent: Parent widget
        width: Figure width in inches
        height: Figure height in inches
        dpi: Figure DPI
    """
    
    def __init__(self, parent=None, width=6, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setMinimumSize(500, 400)
        self.cbar = None
        
    def plot_mode_shape(self, nodes, mode_shape, title=None):
        """
        Plot mode shape with consistent normalization and scaling
        
        Args:
            nodes: Node coordinates array
            mode_shape: Displacement vector for the mode
            title: Plot title
        """
        # Clear previous plot
        self.ax.clear()
        
        # Remove previous colorbar if it exists
        if self.cbar is not None:
            try:
                self.cbar.remove()
            except:
                pass
            self.cbar = None
            
        # Extract unique coordinates
        x_coords = np.unique(nodes[:, 0])
        y_coords = np.unique(nodes[:, 1])
        
        # Create meshgrid for contour plot
        X, Y = np.meshgrid(x_coords, y_coords)
        Z = np.zeros_like(X)
        
        # Map displacement to grid
        for i, (x, y) in enumerate(nodes):
            # Find indices in the grid
            x_idx = np.where(np.isclose(x_coords, x))[0][0]
            y_idx = np.where(np.isclose(y_coords, y))[0][0]
            Z[y_idx, x_idx] = mode_shape[i]
        
        # Create contour plot with fixed normalization
        contour = self.ax.contourf(
            X, Y, Z, 
            levels=np.linspace(-1, 1, 21), 
            cmap=cm.coolwarm,
            vmin=-1,
            vmax=1
        )
        
        # Configure plot
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('X (m)', fontsize=10)
        self.ax.set_ylabel('Y (m)', fontsize=10)
        self.ax.grid(True, linestyle=':', alpha=0.7)
        self.ax.set_xlim(0, np.max(nodes[:, 0]))
        self.ax.set_ylim(0, np.max(nodes[:, 1]))
        
        if title:
            self.ax.set_title(title, fontsize=12, fontweight='bold')
            
        # Add colorbar
        self.cbar = self.fig.colorbar(contour, ax=self.ax, label='Normalized Displacement')
        self.cbar.set_ticks(np.linspace(-1, 1, 11))
        self.draw()