from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import math
import time


class TutorialBot(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()

        # Contants
        self.DODGE_TIME = 0.2

        # Game values
        self.bot_pos = None
        self.bot_yaw = None

        # Dodging
        self.should_dodge = False
        self.on_second_jump = False
        self.next_dodge_time = 0

        # This is just a variable used to make the bot jump every few seconds as a demonstration.
        # This isn't used for anything else, so you can remove it (and the code block that contains this
        # variable (line 68-ish)) if you don't want to see the bot jump every few seconds
        self.dodge_interval = 0

    def aim(self, target_x, target_y):
        angle_between_bot_and_target = math.atan2(target_y - self.bot_pos.y,
                                                target_x - self.bot_pos.x)

        angle_front_to_target = angle_between_bot_and_target - self.bot_yaw

        # Correct the values
        if angle_front_to_target < -math.pi:
            angle_front_to_target += 2 * math.pi
        if angle_front_to_target > math.pi:
            angle_front_to_target -= 2 * math.pi

        if angle_front_to_target < math.radians(-10):
            # If the target is more than 10 degrees right from the centre, steer left
            self.controller.steer = -1
        elif angle_front_to_target > math.radians(10):
            # If the target is more than 10 degrees left from the centre, steer right
            self.controller.steer = 1
        else:
            # If the target is less than 10 degrees from the centre, steer straight
            self.controller.steer = 0

    def check_for_dodge(self):
        if self.should_dodge and time.time() > self.next_dodge_time:
            self.controller.jump = True
            self.controller.pitch = -1

            if self.on_second_jump:
                self.on_second_jump = False
                self.should_dodge = False
            else:
                self.on_second_jump = True
                self.next_dodge_time = time.time() + self.DODGE_TIME

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # Update game data variables
        self.bot_yaw = packet.game_cars[self.team].physics.rotation.yaw
        self.bot_pos = packet.game_cars[self.index].physics.location

        # Just making the bot jump every 3 seconds as demonstration. You can remove this if-block and it won't break the code.
        if self.dodge_interval < time.time():
            self.should_dodge = True
            self.dodge_interval = time.time() + 3

        ball_pos = packet.game_ball.physics.location
        self.aim(ball_pos.x, ball_pos.y)

        # This sets self.jump to be active for only 1 frame
        self.controller.jump = 0

        self.check_for_dodge()

        return self.controller
