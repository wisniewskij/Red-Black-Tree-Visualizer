import sys
import pygame
import asyncio
from pygame import Vector2

from controllers.AnimationController import AnimationController
from controllers.EdgeLengthUpdateController import EdgeLengthUpdateController
from controllers.EdgeManager import EdgeManager
from controllers.NodePositionUpdateController import NodePositionUpdateController
from rbt.RedBlackVisualizedTree import RedBlackVisualizedTree
from utility.enums import Color, Operation
from utility.pygame_text_input_master.pygame_textinput import pygame_textinput, TextInputManager

from utility.gui import Button, drawTextWithOutline


class Visualizer:

    def __init__(self):
        # Config
        self.tps_max = 60.0

        # Initialization
        pygame.init()
        pygame.key.set_repeat(200, 250)
        pygame.display.set_caption("Red-black tree visualization")
        pygame.display.set_icon(pygame.image.load('assets/icon.png'))
        self.screen = pygame.display.set_mode((1920, 1080))
        self.tps_clock = pygame.time.Clock()
        self.tps_delta = 0.0

        self.x_offset = 0
        self.y_offset = 0
        self.zoom = 1.0

        self.node_position_update_controller = NodePositionUpdateController()
        self.edge_length_update_controller = EdgeLengthUpdateController()
        self.animation_controller = AnimationController(self)
        self.tree = RedBlackVisualizedTree(self)
        self.edge_manager = EdgeManager(self)

        self.text_input = pygame_textinput.TextInputVisualizer(
            manager=TextInputManager(validator=lambda input_arg: len(input_arg) <= 5 and
                                                                 (input_arg == '' or (input_arg[0] == '-' or input_arg[
                                                                     0].isdigit()) and (
                                                                          len(input_arg) == 1) or input_arg[
                                                                                                  1:].isdigit())
                                     ),
            antialias=True,
            font_object=pygame.font.SysFont('Helvetica', 90)
        )

        self.add_value_button = Button(self, 0, self.screen.get_height() - 90, 200, 90,
                                       'Add value: ', 'Arial', 40, Color.RED.value, Color.WHITE.value)

    # Main loop
    async def run(self):
        while True:
            # Mouse position
            mouse_pos = pygame.mouse.get_pos()

            # Handle events
            events = pygame.event.get()
            for event in events:
                if (event.type == pygame.QUIT or
                        (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.check_for_value_add()

                    if event.key == pygame.K_r:
                        self.restart()
                    if event.key == pygame.K_c:
                        self.animation_controller.add_animated_element((Operation.CHANGE_COLOR, None, 20))
                    if event.key == pygame.K_b:
                        self.tree.bfs_reposition()
                    if event.key == pygame.K_SPACE:
                        self.x_offset = 0
                        self.y_offset = 0
                        self.zoom = 1.0

                        nodes = self.tree.get_nodes()
                        while True:
                            for node in nodes:
                                if (node.position[0] - node.radius < 0 or
                                        node.position[0] + node.radius > self.screen.get_width() or
                                        node.position[1] - node.radius < 0 or
                                        node.position[1] + node.radius > self.screen.get_height()
                                ):
                                    self.zoom /= 1.2
                            else:
                                break

                        screen_center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
                        self.x_offset -= (screen_center[0] * (self.zoom - 1.0)) / self.zoom
                        self.y_offset -= (screen_center[1] * (self.zoom - 1.0)) / self.zoom

                elif event.type == pygame.MOUSEBUTTONDOWN and self.animation_controller.idle():
                    if event.button == 1:
                        nodes = self.tree.get_nodes()
                        for node in nodes:
                            if Vector2(node.get_transformed_position()).distance_to(Vector2(mouse_pos)) < node.radius:
                                self.tree.delete_all(node)

                        if self.add_value_button.rect.collidepoint(mouse_pos):
                            self.check_for_value_add()

            # Update text_input
            self.text_input.update(events)

            # Ticking
            self.tps_delta += self.tps_clock.tick() / 1000.0
            while self.tps_delta > 1 / self.tps_max:
                self.tps_delta -= 1 / self.tps_max
                self.tick()

            # Rendering
            self.screen.fill(Color.LIGHT_BLUE.value)
            self.draw()
            pygame.display.update()

            await asyncio.sleep(0)

    def tick(self):
        self.tree.update()
        self.node_position_update_controller.update()
        self.animation_controller.update()
        self.edge_length_update_controller.update()
        self.edge_manager.update()

        # Checking inputs
        keys = pygame.key.get_pressed()
        if keys[pygame.K_n] or keys[pygame.K_m]:
            screen_center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
            old_zoom = self.zoom
            if keys[pygame.K_m]:
                self.zoom += 0.04 / (self.tps_max / 60)
                self.zoom = min(self.zoom, 4)
            if keys[pygame.K_n]:
                self.zoom -= 0.04 / (self.tps_max / 60)
                self.zoom = max(0.1, self.zoom)
            new_zoom = self.zoom
            delta_zoom = new_zoom / old_zoom
            self.x_offset -= (screen_center[0] * (delta_zoom - 1.0)) / self.zoom
            self.y_offset -= (screen_center[1] * (delta_zoom - 1.0)) / self.zoom

        if keys[pygame.K_LEFT]:
            self.x_offset += min(max(int(10 * 1 / self.zoom), 10), 100) / (self.tps_max / 60)
        if keys[pygame.K_RIGHT]:
            self.x_offset -= min(max(int(10 * 1 / self.zoom), 10), 100) / (self.tps_max / 60)
        if keys[pygame.K_UP]:
            self.y_offset += min(max(int(10 * 1 / self.zoom), 10), 100) / (self.tps_max / 60)
        if keys[pygame.K_DOWN]:
            self.y_offset -= min(max(int(10 * 1 / self.zoom), 10), 100) / (self.tps_max / 60)

    def draw(self):
        if self.animation_controller.idle():  #debug
            self.tps_max = 60.0

        nodes = list(reversed(self.tree.get_nodes_bfs()))
        nodes_being_deleted = list(self.tree.nodes_being_deleted)
        newly_added_nodes = [node for node in nodes if node.recently_added]
        old_nodes = [node for node in nodes if not node.recently_added]
        nodes = nodes_being_deleted + newly_added_nodes + old_nodes

        self.edge_manager.draw()

        for node in nodes:
            node.draw()
        self.add_value_button.draw()
        self.screen.blit(self.text_input.surface, (200, self.screen.get_height() - 96))

        # tmp
        if not self.animation_controller.idle():
            # pygame.draw.circle(self.screen, Color.RED.value, (self.screen.get_width(), self.screen.get_height()), 50)
            drawTextWithOutline(self, 'Processing...', 'Helvetica', 80,
                                Color.RED.value, self.screen.get_width()//2, self.screen.get_height() - 96)
        else:
            for new_node in newly_added_nodes:
                new_node.recently_added = False

    def restart(self):
        self.node_position_update_controller = NodePositionUpdateController()
        self.edge_length_update_controller = EdgeLengthUpdateController()
        self.animation_controller = AnimationController(self)
        self.tree = RedBlackVisualizedTree(self)
        self.edge_manager = EdgeManager(self)

    def check_for_value_add(self):
        if (
                self.animation_controller.idle()
                and self.text_input.value != ''
                and self.text_input.value != '-'
        ):
            self.tree.insert(int(self.text_input.value))
            self.text_input.value = ''
            if len(self.tree) == 1:
                self.x_offset = 0
                self.y_offset = 0
                self.zoom = 1.0
