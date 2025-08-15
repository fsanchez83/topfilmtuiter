import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np


class InfiniteSquareAnimation:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-2, 2)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_facecolor('black')

        # Parámetros de la animación
        self.zoom_factor = 1.12  # Factor de zoom por frame (más agresivo)
        self.rotation_angle = 0  # Ángulo de rotación actual
        self.zoom_count = 0  # Contador de zooms
        self.max_zooms = 45  # Frames hasta el primer reset
        self.current_scale = 1.0  # Escala actual

    def draw_nested_squares(self, scale, rotation, depth=3):
        """Dibuja cuadrados anidados con la escala y rotación dadas"""
        colors = ['cyan', 'cyan', 'cyan']  # Colores más visibles

        for i in range(depth):
            if i == 0:
                # Cuadrado exterior
                current_scale = scale
            elif i == 1:
                # Cuadrado interior: tamaño mínimo de píxel (aproximadamente 0.01 en coordenadas)
                current_scale = scale * 0.01  # 1% del tamaño original
            else:
                # Cuadrados aún más pequeños para el efecto
                current_scale = scale * (0.01 ** i)

            # Solo dibujar cuadrados que sean visibles
            if current_scale > 0.005:
                # Crear el cuadrado
                square = patches.Rectangle(
                    (-current_scale / 2, -current_scale / 2),
                    current_scale,
                    current_scale,
                    linewidth=max(0.5, 3 - i),
                    # Líneas más gruesas para cuadrados grandes
                    edgecolor=colors[i % len(colors)],
                    facecolor='none',
                    alpha=1.0
                )

                # Aplicar rotación
                if rotation != 0:
                    t = plt.matplotlib.transforms.Affine2D().rotate_deg(
                        rotation) + self.ax.transData
                    square.set_transform(t)

                self.ax.add_patch(square)

    def animate(self, frame):
        """Función de animación llamada en cada frame"""
        self.ax.clear()
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-2, 2)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_facecolor('black')

        # Calcular el progreso del zoom
        zoom_progress = frame % self.max_zooms

        # Aplicar zoom de acercamiento (los cuadrados se hacen más grandes)
        # El cuadrado debe crecer hasta salirse completamente del cuadro
        zoom_scale = self.zoom_factor ** zoom_progress
        current_scale = 1.5 * zoom_scale  # Empezamos con 1.5 para llegar a ~6-8 (se sale del cuadro)

        # Cada 60 frames (3 zooms visuales), rotamos 90 grados
        rotation_cycle = frame // self.max_zooms
        current_rotation = (rotation_cycle * 90) % 360

        # Dibujar los cuadrados anidados
        self.draw_nested_squares(current_scale, current_rotation)

        # Añadir título con información del estado
        cycle_number = (frame // self.max_zooms) + 1
        zoom_percentage = (zoom_progress / self.max_zooms) * 100

        if zoom_progress > 40:  # Últimos frames antes de rotar
            title = f"¡ROTANDO! - Ciclo {cycle_number}"
        elif zoom_percentage > 80:
            title = f"SALIENDO DEL CUADRO... - Ciclo {cycle_number}"
        elif zoom_percentage > 50:
            title = f"CRECIENDO... - Ciclo {cycle_number}"
        else:
            title = f"ACERCÁNDOSE... - Ciclo {cycle_number}"

        self.ax.set_title(title, color='white', fontsize=14, pad=20)

    def create_animation(self, frames=240, interval=100):
        """Crear y retornar la animación"""
        anim = FuncAnimation(
            self.fig,
            self.animate,
            frames=frames,
            interval=interval,
            repeat=True,
            blit=False
        )
        return anim

    def save_gif(self, filename='infinite_square.gif', frames=240, interval=100):
        """Guardar la animación como GIF"""
        print("Creando animación...")
        anim = self.create_animation(frames, interval)

        print(f"Guardando como {filename}...")
        anim.save(filename, writer='pillow', fps=10, dpi=80)
        print(f"¡Animación guardada como {filename}!")

        # Mostrar la animación
        plt.show()


# Crear y ejecutar la animación
if __name__ == "__main__":
    # Crear la instancia de la animación
    animation = InfiniteSquareAnimation()

    # Guardar como GIF (240 frames = 4 ciclos completos)
    animation.save_gif('cuadrado_infinito.gif', frames=240, interval=100)

