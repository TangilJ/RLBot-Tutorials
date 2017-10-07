import math
import time

BOT_NAME = "LiningUpShotsBot"  # You can change this string, if you wish

class agent:
    def __init__(self, team):
        self.team = team

        # Controller inputs
        self.stick_x = 16383
        self.stick_y = 16383

        # Game data
        self.bot_pos_x = 0
        self.bot_pos_y = 0
        self.bot_yaw = 0
        self.ball_pos_x = 0
        self.ball_pos_y = 0

        self.MAXIMUM_DISTANCE_TO_CHASE_TARGET = 750

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

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def closest_point(self, x1, y1, x2, y2, x3, y3):
        k = ((y2 - y1) * (x3 - x1) - (x2 - x1) * (y3 - y1)) / ((y2 - y1) ** 2 + (x2 - x1) ** 2)
        x4 = x3 - k * (y2 - y1)
        y4 = y3 + k * (x2 - x1)

        return x4, y4

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

        if (self.team == "blue" and self.bot_pos_y < self.ball_pos_y) or (self.team == "orange" and self.bot_pos_y > self.ball_pos_y):
            if self.team == "blue":
                enemy_goal = 5000
            else:
                enemy_goal = -5000
            
            # target is the closest point (on the line through the goal and the ball) from the bot
            target = self.closest_point(0, enemy_goal,
                                        self.ball_pos_x, self.ball_pos_y,
                                        self.bot_pos_x, self.bot_pos_y)

            if self.distance(target[0], target[1], self.bot_pos_x, self.bot_pos_y) > self.MAXIMUM_DISTANCE_TO_CHASE_TARGET:
                # Go to the target if far away enough
                self.aim(target[0], target[1])
            else:
                # Chase ball if close to ball
                self.aim(self.ball_pos_x, self.ball_pos_y)

        else:
            # Blue has their goal at -5000 (Y axis) and orange has their goal at 5000 (Y axis). This means that:
            # - Blue is behind the ball if the ball's Y axis is greater than blue's Y axis
            # - Orange is behind the ball if the ball's Y axis is smaller than orange's Y axis
            if self.team == "blue":
                # Blue team's goal is located at (0, 0, -5000)
                self.aim(0, -5000)
            else:
                # Orange team's goal is located at (0, 0, 5000)
                self.aim(0, 5000)

        return [self.stick_x, self.stick_y,
                32767, 0, 0, 0, 0]
