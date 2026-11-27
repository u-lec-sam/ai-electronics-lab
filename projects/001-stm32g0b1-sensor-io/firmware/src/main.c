/* AEL-001 portable application scaffold; not a flashable target image yet. */
#include <stdint.h>

typedef struct {
    uint32_t heartbeat_count;
    uint8_t sensor_bus_ready;
} ael_app_state_t;

static ael_app_state_t app;

static void app_init(void)
{
    app.heartbeat_count = 0U;
    app.sensor_bus_ready = 0U;
}

/* Board-specific GPIO, timer, and I2C drivers will be connected here. */
static void app_process(void)
{
    app.heartbeat_count++;
}

int main(void)
{
    app_init();
    for (;;) {
        app_process();
    }
}
