import math

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

        self.aim(self.ball_pos_x, self.ball_pos_y)
        self.acceleration = 32767

        return [self.stick_x, self.stick_y,
                self.acceleration, self.deceleration,
                self.jump, self.boost, self.powerslide]
