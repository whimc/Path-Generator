# API Lander page

***

## Generate path map images
```
/pathgenerator
```

### Parameters

| Name          | Type      | Description |
|---------------|-----------|-------------|
| `username`    | `string`  | **Required.** Username of player |
| `start_time`  | `int`     | **Required.** Unix timestamp of start time |
| `end_time`    | `int`     | **Required.** Unix timestamp of end time |
| `gen_empty`   | `bool`    | Whether or not to generate empty images with no interaction. Default: `false` |

### Examples
Generate images that exist for `Poi` between times `1570000000` and `1582000000`
```
api.henhapl.me/pathgenerator?username=Poi&start_time=1570000000&end_time=1582000000
```

Generate images (even if they don't exist) for `Notch` between times `0` and `1`.
```
api.henhapl.me/pathgenerator?username=Notch&start_time=0&end_time=1&gen_empty=true
```