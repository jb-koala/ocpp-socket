// ESP32-S3 entry point. Hardware-dependent code lives here; business logic in lib/.
#include <stdio.h>
#include "esp_log.h"
#include "esp_ota_ops.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "session_guard.h"

#ifndef GIT_COMMIT
#define GIT_COMMIT "unknown"
#endif

static const char *TAG = "main";

void app_main(void) {
    // Etapa 8: la placa imprime el commit al bootear. Se verifica antes de leer cualquier log.
    printf("\n=== ocpp-socket fw commit=%s ===\n", GIT_COMMIT);
    ESP_LOGI(TAG, "boot commit=%s", GIT_COMMIT);

    // OTA rollback (REQ002): confirm this image only once the app is known-good.
    // TODO: move after CSMS connection succeeds.
    esp_ota_mark_app_valid_cancel_rollback();

    sg_t guard;
    sg_init(&guard, (uint32_t)(xTaskGetTickCount() * portTICK_PERIOD_MS));

    // TODO: wifi + websocket + OCPP 1.6-J (REQ001), meter (REQ003), relay driver.
    printf("READY\n");  // pytest-embedded waits for this line (etapa 8)

    for (;;) {
        // TODO: float t = ntc_read_c(); sg_action_t a = sg_update(&guard, t, now_ms); ...
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
