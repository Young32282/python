#include <stdio.h>
#include <math.h>

int main() {
    double v = 500.0;
    double angle_degrees = 22.8;
    double angle_radians = angle_degrees * 3.1415962 / 180.0; 
    double t_start = 0.0, t_end = 10.0, t_increment = 0.5;

    for (double t = t_start; t <= t_end; t += t_increment) {
        double x = v * t * cos(angle_radians);
        double y = v * t * sin(angle_radians);
        printf("%.1f,%.2f,%.2f\n", t, x, y);
    }

    return 0;
}