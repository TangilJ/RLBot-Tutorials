import math
import time

BOT_NAME = "TutorialBot"  # You can change this string, if you wish

class agent:
    def __init__(self, team):
        self.team = team

        # Controller inputs
        self.stick_x = 16383
        self.stick_y = 16383
        self.acceleration = 0
        self.deceleration = 0
        self.boost = 0
        self.jump = 0
        self.powerslide = 0

        # Game data
        self.bot_pos_x = 0
        self.bot_pos_y = 0
        self.bot_yaw = 0
        self.ball_pos_x = 0
        self.ball_pos_y = 0

        # Dodging
        self.should_dodge = False
        self.on_second_jump = False
        self.next_dodge_time = 0

        # This is just a variable used to make the bot jump every few seconds as a demonstration.
        # This isn't used for anything else, so you can remove it (and the code block that contains this
        # variable (line 95-ish)) if you don't want to see the bot jump every few seconds
        self.dodge_interval = 0

    def aim(self, target_x, target_y):
        angle_between_bot_and_target = math.degrees(math.atan2(target_x - self.bot_pos_x,
                                                               target_y - self.bot_pos_y))

        angle_front_to_target = angle_between_bot_and_target - self.bot_yaw * -1

        # Correct the values
        if angle_front_to_target < -180:
            angle_front_to_target += 360
        if angle_front_to_target > 180:
            angle_front_to_target -= 360

        if angle_front_to_target < -10:
            # If the target is more than 10 degrees left from the centre, steer right
            self.stick_x = 32767
        elif angle_front_to_target > 10:
            # If the target is more than 10 degrees right from the centre, steer left
            self.stick_x = 0
        else:
            # If the target is less than 10 degrees from the centre, steer straight
            self.stick_x = 16383

    def dodge(self, target_x, target_y):
        if self.should_dodge and time.time() > self.next_dodge_time:
            self.aim(target_x, target_y)
            self.jump = 1
            self.stick_y = 0

            if self.on_second_jump:
                self.on_second_jump = False
                self.should_dodge = False
            else:
                self.on_second_jump = True
                self.next_dodge_time = time.time() + 0.2

    def get_output_vector(self, values):
        data = values.GameTickPacket

        # Update ball positions
        self.ball_pos_x = data.gameball.Location.X
        self.ball_pos_y = data.gameball.Location.Y  # Y axis is not height here! Z axis is height.

        # Update bot positions and rotations depending on the bot's team
        if self.team == "blue":
            team_index = 0
        else:
            team_index = 1

        self.bot_pos_x = data.gamecars[team_index].Location.X
        self.bot_pos_y = data.gamecars[team_index].Location.Y

        # Convert the game's rotation values to degrees
        self.bot_yaw = abs(data.gamecars[team_index].Rotation.Yaw) % 65536 / 65536 * 360
        if data.gamecars[team_index].Rotation.Yaw < 0:
            self.bot_yaw *= -1
        # Make 0 degrees the centre of the circle
        self.bot_yaw = (self.bot_yaw + 90) % 360 - 180

        # Just making the bot jump every 3 seconds as demonstration. You can remove this if-block and it won't break the code.
        if self.dodge_interval < time.time():
            self.should_dodge = True
            self.dodge_interval = time.time() + 3

        # This sets self.jump to be active for only 1 frame
        self.jump = 0

        self.dodge(self.ball_pos_x, self.ball_pos_y)

        return [self.stick_x, self.stick_y,
                self.acceleration, self.deceleration,
                self.jump, self.boost, self.powerslide]
