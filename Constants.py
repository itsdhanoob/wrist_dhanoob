POSITION_OFFSET_DOC = 2048*(4.4/2048)  # convert encoder ticks to radians
POSITION_OFFSET_PAT = 2048*(2.2/2048) 

KP = 0.4        # determines the system's response time (small kp = slow response time, large kp = oscillation)
KD = 0          # improves setteling time and stability by damping overshoot ()
KI = 1          # reduces the steady state error ie velocity_error, postion_error 

current_threshold = 30


