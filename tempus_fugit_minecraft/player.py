from tempus_fugit_minecraft.utilities import BRICK, GRASS, SAND
import math

class Player:
    def __init__(self):
        # About the height of a block.
        self.MAX_JUMP_HEIGHT = 1.0 
        self.MAX_FALL_SPEED = 50
        self.FLYING_SPEED = 15
        self.GRAVITY = 20.0
        # To derive the formula for calculating jump speed, first solve
        #    v_t = v_0 + a * t
        # for the time at which you achieve maximum height, where a is the acceleration
        # due to gravity and v_t = 0. This gives:
        #    t = - v_0 / a
        # Use t and the desired MAX_JUMP_HEIGHT to solve for v_0 (jump speed) in
        #    s = s_0 + v_0 * t + (a * t^2) / 2
        self.JUMP_SPEED = math.sqrt(2 * self.GRAVITY * self.MAX_JUMP_HEIGHT)
        self.PLAYER_HEIGHT = 2
        self.WALK_SPEED_INCREMENT = 5

        self.walking_speed = self.WALK_SPEED_INCREMENT
        # When flying gravity has no effect and speed is increased.
        self.flying = False
        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = [0, 0]
        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        self.position = (0, 0, 0)
        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation = (0, 0)
        # Velocity in the y (upward) direction.
        self.dy = 0
        # A list of blocks the player can place. Hit num keys to cycle.
        self.inventory = [BRICK, GRASS, SAND]
        # The current block the user can place. Hit num keys to cycle.
        self.block = self.inventory[0]

    def get_sight_vector(self) -> tuple:
        """Returns the current line of sight vector indicating the direction the player is looking."""
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return dx, dy, dz
    
    def get_motion_vector(self) -> tuple:
        """Returns the current motion vector indicating the velocity of the player.

        Returns
        -------
        vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.
        """
        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0:
                    # Moving backwards.
                    dy *= -1
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return dx, dy, dz
    
    def speed_up(self) -> None:
        """Increases the walking speed of the player."""
        if self.walking_speed <= 15:
            self.walking_speed += self.WALK_SPEED_INCREMENT

    def speed_down(self):
        if self.walking_speed > 5:
            self.walking_speed -= self.WALK_SPEED_INCREMENT

    def move_forward(self):
        self.strafe[0] -= 1
    
    def move_backward(self):
        self.strafe[0] += 1

    def move_left(self):
        self.strafe[1] -= 1

    def move_right(self):
        self.strafe[1] += 1

    def jump(self):
        if self.dy == 0:
            self.dy = self.JUMP_SPEED

    def select_active_item(self, index):
        selected_index = index % len(self.inventory)
        self.block = self.inventory[selected_index]

    def stop_forward(self):
        self.strafe[0] += 1
    
    def stop_backward(self):
        self.strafe[0] -= 1

    def stop_left(self):
        self.strafe[1] += 1

    def stop_right(self):
        self.strafe[1] -= 1

    def adjust_sight(self, dx, dy):
        x, y = self.rotation
        m = 0.15
        x = dx * m + x
        y = dy * m + y
        y = max(-90, min(90, y))
        self.rotation = (x, y)

    def current_speed(self):
        return self.FLYING_SPEED if self.flying else self.walking_speed
    
    def toggle_flight(self):
        self.flying = not self.flying