import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh

class FEMPlateModalAnalysis:
    """
    Performs FEM modal analysis for 2D rectangular plates using Kirchhoff plate theory.
    
    Attributes:
        length (float): Plate length in meters
        width (float): Plate width in meters
        nx (int): Number of elements in x-direction
        ny (int): Number of elements in y-direction
        E (float): Young's modulus in Pascals
        nu (float): Poisson's ratio
        rho (float): Material density in kg/m³
        thickness (float): Plate thickness in meters
    """
    
    def __init__(self, length, width, nx, ny, E, nu, rho, thickness):
        self.length = length
        self.width = width
        self.nx = nx
        self.ny = ny
        self.E = E
        self.nu = nu
        self.rho = rho
        self.thickness = thickness
        
        # Precomputed values
        self.D = E * thickness**3 / (12 * (1 - nu**2))  # Flexural rigidity
        self.num_nodes = (nx + 1) * (ny + 1)
        self.num_elements = nx * ny
        self.nodes = None
        self.elements = None
        self.dx = length / nx
        self.dy = width / ny
        
    def generate_mesh(self):
        """Generate structured quadrilateral mesh"""
        x = np.linspace(0, self.length, self.nx + 1)
        y = np.linspace(0, self.width, self.ny + 1)
        self.nodes = np.array([[xi, yi] for yi in y for xi in x])
        
        self.elements = []
        for j in range(self.ny):
            for i in range(self.nx):
                n1 = j * (self.nx + 1) + i
                n2 = j * (self.nx + 1) + i + 1
                n3 = (j + 1) * (self.nx + 1) + i + 1
                n4 = (j + 1) * (self.nx + 1) + i
                self.elements.append([n1, n2, n3, n4])
                
    def apply_boundary_conditions(self, fixed_edges):
        """Identify fixed nodes based on selected edges"""
        fixed_nodes = set()
        
        if 'left' in fixed_edges:
            fixed_nodes |= {i for i in range(0, self.num_nodes, self.nx + 1)}
        if 'right' in fixed_edges:
            fixed_nodes |= {i for i in range(self.nx, self.num_nodes, self.nx + 1)}
        if 'top' in fixed_edges:
            fixed_nodes |= {i for i in range(self.num_nodes - (self.nx + 1), self.num_nodes)}
        if 'bottom' in fixed_edges:
            fixed_nodes |= {i for i in range(0, self.nx + 1)}
            
        return sorted(fixed_nodes)
    
    def compute_element_matrices(self):
        """Compute consistent mass and stiffness matrices for plate elements"""
        # Consistent mass matrix for plate element
        me = self.rho * self.thickness * self.dx * self.dy / 36 * np.array([
            [4, 2, 1, 2],
            [2, 4, 2, 1],
            [1, 2, 4, 2],
            [2, 1, 2, 4]
        ])
        
        # Stiffness matrix for plate bending
        factor = self.D * self.dx * self.dy
        ke = factor * np.array([
            [4, -1, -2, -1],
            [-1, 4, -1, -2],
            [-2, -1, 4, -1],
            [-1, -2, -1, 4]
        ]) / (self.dx * self.dy)
        
        return ke, me
    
    def assemble_global_matrices(self):
        """Assemble global stiffness and mass matrices"""
        dof_per_node = 1  # Transverse displacement only
        total_dof = self.num_nodes * dof_per_node
        
        # Initialize global matrices
        K = sp.lil_matrix((total_dof, total_dof))
        M = sp.lil_matrix((total_dof, total_dof))
        
        # Get element matrices
        ke, me = self.compute_element_matrices()
        
        # Assemble matrices
        for elem in self.elements:
            for i, ni in enumerate(elem):
                for j, nj in enumerate(elem):
                    K[ni, nj] += ke[i, j]
                    M[ni, nj] += me[i, j]
        
        return K.tocsc(), M.tocsc()
    
    def solve_modes(self, num_modes, fixed_edges):
        """Solve eigenvalue problem for natural frequencies and mode shapes"""
        self.generate_mesh()
        K, M = self.assemble_global_matrices()
        
        # Apply boundary conditions
        fixed_nodes = self.apply_boundary_conditions(fixed_edges)
        free_dofs = [i for i in range(self.num_nodes) if i not in fixed_nodes]
        
        # Reduce matrices
        K_red = K[free_dofs, :][:, free_dofs]
        M_red = M[free_dofs, :][:, free_dofs]
        
        # Solve eigenvalue problem
        eigenvalues, eigenvectors = eigsh(
            K_red, 
            k=num_modes, 
            M=M_red, 
            sigma=0, 
            which='LM',
            tol=1e-6,
            maxiter=1000
        )
        
        # Process results
        frequencies = np.sqrt(np.abs(eigenvalues)) / (2 * np.pi)
        sorted_indices = np.argsort(frequencies)
        frequencies = frequencies[sorted_indices]
        
        # Expand mode shapes to full DOF and normalize
        mode_shapes = np.zeros((self.num_nodes, num_modes))
        for i, idx in enumerate(sorted_indices):
            mode = eigenvectors[:, idx]
            # Normalize by maximum displacement
            max_disp = np.max(np.abs(mode))
            if max_disp > 1e-10:
                mode /= max_disp
            mode_shapes[free_dofs, i] = mode
        
        return frequencies, mode_shapes