# Haystack File for Optima

#Hierarchical Structure 
```txt
Main Menu - id:@100
|
1-  FanSpeed {reg:4x100, 0=OFF, 1-4=Levels} - id:@101
|   1-- Standby - id:@1011
|   2-- Fan Speed Level 1 - id: @1012
|   3-- Fan Speed Level 2 - id: @1013
|   4-- Fan Speed Level 3 - id: @1014
|   5-- Fan Speed Level 4 - id: @1015
|
2-- Temperature - id: @102
|   1-- Room Temperature {reg:4x00, unit:°C, range:[10 30], decimal:1} - id: @1021
|   2-- T2 adjustment {reg:4x12, unit:°C, range:[-5 0], decimal:1} - id: @1022
|
3-- System Status (Read-Only) - id: @103
|   1-- Sensors - id @1031
|       1-- T2-panel - Room Temperature {reg:3x09, unit:°C, range:[-30 70]} - id: @10311 
|       2-- T1 - Supply air {reg:3X00, unit:°C, range:[-30 70]} - id: @10312
|       3-- T3 - Fresh air {reg:3x02, unit:°C, range:[-30 70]} - id: @10313
|       4-- T4 - Exhaust air {reg:3x03, unit:°C, range:[-30 70]} - id: @10314
|       5-- T7 - Extract air {reg:3x06, unit:°C, range:[-30 70]} - id: @10315
|       6-- T8 - Frost {reg:3x07, unit:°C, range:[-30 70]} - id : @10316
|       7-- T9 - Extra Sensor {reg:3x08, unit:°C, range:[-30 70]} - id: @10317
|       8-- Humidity Sensor {reg:3x10, unit:%, range:[0 100]} - id: @10318
|       9-- Humidity Setpoint(calc) {reg:3x11. unit:%, range:[0 100]} - id: @10319
|       
|   2-- Fans - id: @1032
|       1-- Supply fan airflow {reg:3X102, unit:%, range:[0 100]} - id: @10321
|       2-- Supply fanspeed {reg:3x108, unit:rpm, range:[0 9999]} - id: @10322
|       3-- Extract fan airflow {reg:3x103, unit:%, range:[0 100]} - id: @10323
|       4-- Extract fanspeed {reg:3x109, unit: rpm, range:[0 9999]} - id: @10324 
|       5-- Humidity fan control {reg:3x106, unit:%, range:[0 100]} - id: @10325
|       6-- ByPass {reg:3x107, OFF=0, ON=1} - id: @10326
|       7-- ByPass rate {reg:3x104, unit:%, range:[0 100]} - id: @10327
|       8-- WaterValve {reg:3x105. unit:%, range:[0 100]} - id: @10328
|
|   3-- Alarms {reg:3x101} (to be added in haystack file) - id: @1033
|       1-- Stop Control {0=OFF, 1=ON, bitmask:bit0(value=1)} - id: @10331
|       2-- Change filter {0=OFF, 1= ON, bitmask:bit1(value=2)} - id: @10332 
|       3-- Frost {0=OFF, 1=ON, bitmask:bit8(value=8)} - id: @10333
|       4-- Comm error {0=OFF, 1=ON, bitmask:bit4(value=16)} - id: @10334
|   
|   4-- Fire Test (to be added in haystack file) - id: @1034
|       1-- Fire Alarm com_status {reg:3x16, bit0=Err at SPJ-1, bit1=Err at SPJ-2, bit3=Err at SPJ-3, bit4=Err at SPJ-4, bit5-6=Err at Box1, bit7-8=Err at Box2} - id: @10341
|       2-- Fire Test-Results {reg:3x17, bit0=Err at SPJ1, bit1=Err at SPJ-2, bit3=Err at SPJ-3, bit4=Err at SPJ-4, bit7=Test OK} - id: @10342
|       3-- Fire Test-Date {reg:3x18} - id: @10343
|       4-- Fire Test-Month {reg:3x19} - id: @10344
|       5-- Fire Test-Year {reg:3x20} - id: @10345
|       6-- Fire Test-time {reg:3x21} - id: @10346
|       7-- Fire Test-minute {reg:3x22} - id: @10347
|       8-- Fire Test Err {reg:3x23, bit0=Err at SPJ-1, bit1=Err at SPJ-2, bit3=Err at SPJ-3, bit4=Err at SPJ-4} - id: @10348
|
4-- System Settings (Writable) - id: @104
|   1-- User - id: @1041
|       1-- Heat {reg:4x102} - id:@10411
|       2-- Heat Timer {reg:4x106, 0=OFF, 1-9(hours)} - id:@10412
|       3-- Preheat {reg:4x01, 0=0FF, 1-2(modes)} - id:@10413
|       4-- Reheat {reg:4x02, 0=OFF, 1=ON} - id:@10414
|       5-- Humidity {reg:4x05, 0=OFF, 1=ON} - id:@10415
|       6-- Timer levels 3 and 4 - id: @10416
|           1-- Timer levels 3 and 4 {reg:4x03, 0=OFF, 1=ON} - id: @104161
|           2-- Timer levels 3 and 4 {reg:4x13, 1-9(hours)} - id: @104162
|       7-- Filter - id: @10417
|           1-- Filter reset {reg:4x105, 0=OFF, 1=RESET} - id: @104171
|           2-- Filter change autostop {reg:4x14, 0=OFF, 1=ON} - id: @104172
|           3-- Filter change {reg: 4x04, unit:months,range:[0 6]} - id: @104173
|       8-- Humidity Control - id: @10418
|           1-- Humidity max temperature {reg:4x28, unit:°C, range:[5 25]} - id: @104181
|           2-- Humidity max value {reg:4x29, unit:%, range:[35 85]} - id: @104182
|           3-- Humidity fanspeed {reg:4x30, unit:rpm, range:[5 20]} - id: @104183
|           4-- Humidity regulating frequency {reg:4x31, unit:mins,range[1 60]} - id: @104184
|
|   2-- Service - id: @1042
|       1-- FanSpeed Levels - id: @10421
|           1-- Supply air levels  - id: @104211
|               1-- Level 1 {reg:4x06, unit:%, range:[0 100]} - id: @1042111
|               2-- Level 2 {reg:4x07, unit:%, range:[0 100]} - id: @1042112
|               3-- Level 3 {reg:4x08, unit:%, range:[0 100]} - id: @1042113
|           2-- Extract air levels  - id: @104212
|               1-- Level 1 {reg:4x09, unit:%, range:[0 100]} - id: @1042121
|               2-- Level 2 {reg:4x10, unit:%, range:[0 100]} - id: @1042122
|               3-- Level 3 {reg:4x11, unit:%, range:[0 100]} - id: @1042123
|       2-- Regulator  - id: @10422
|           1-- Frost {reg:4x21, 0=OFF, 1=ON} - id: @104221
|           2-- Frost reduction {reg:4x20, unit:°C, range:[0 10], decimal:1} - id: @104222
|           3-- Regulation form {reg:4x15, 0=Room, 1=Supply, 2=External} - id: @104223
|           4-- Aux Relay {reg:4x23, range:[0 5]} - id: @104224
|           5-- Water Regulation Interval {reg:4x18, unit:secs, range:[1 250]} - id: @104225
|           6-- Frost Default {reg:4x22, unit:°C, range:[0 10], decimal:1} - id: @104226
|           7-- System Stop {reg:4x24, 0=OFF, 1=ON} - id: @104227
|           8-- Right/Left Model {reg:4x32, 0=Right, 1=Left} - id: @104228
|       3-- Electric Heating - id: @10423
|           1-- Power Regulation Interval {reg:4x19, unit:mins, range:[1 30]} - id: @104231
|           2-- Preheat PI P {reg:4x33, range:[1 255]} - id: @104232
|           3-- Preheat PI I {reg:3x34, range:[1 255]} - id: @104233
|           4-- Preheat temperature {reg:4x16, unit:°C, range:[-15.0 0], decimal:1} - id: @104234
|           5-- Preheat regulation {reg:4x35, unit:secs, range:[10 120]} - id: @104235
|           6-- Reheat Offset {reg:4x36, unit:°C, range:[15 40], decimal:1} - id: @104236
|           7-- Reheat PI P {reg:4x37, range:[1 255]} - id: @104237
|           8-- Reheat PI I {reg:4x38, range:[1 255]} - id: @104238
|           9-- Reheat regulation {reg:4x39, unit:secs, range:[10 120]} - id: @104239
|       4-- ByPass - id: @10424
|           1-- ByPass Max {reg:4x17, unit:°C, range:[1.0 10.0], decimal=1} - id: @104241
|           2-- End ByPass T3(Fresh Air) {reg:4x25, unit:°C, range:[0 20]} - id: @104242
|       5-- Fire Control - id: @10425
|           1-- Demand CNTRL(Behovsstyring) {reg:4x40, range:[0 100]} - id: @104251
|           2-- Number of FireDampers {reg:4x41, range:[1-4], 0=OFF} - id: @104252
|           3-- Damper test {reg=4x42, 0=OFF, 1=TEST} - id: @104253
|           4-- Damper test day {reg:4x43, 0=Monday...7=Sunday} - id: @104254
|           5-- Damper test hour {reg:4x44, unit:hours, range:[0 23]} - id: @104255
|       6-- Modbus - id: @10426
|           1-- Modbus Mode {reg:4x26, 0=OFF, 1=9600, 2=19200} - id: @104261
|           2-- Modbus Slave Address {reg:4x27, range[0 247]} - id: @104262
```