# Better11
An all around windows 11 system enhancer that includes live and offline image editing and application downloader/installer

## Deployment
Better11 includes CLI helpers for capturing and applying Windows images as well as servicing offline images.

### Capture a volume to WIM or ESD
```bash
python -m better11.cli deploy capture \
  --volume C:\\ \
  --image C:\\images\\install.wim \
  --name "MyImage" \
  --description "Captured from reference machine" \
  --format wim
```

### Apply an image to a target
```bash
python -m better11.cli deploy apply \
  --image C:\\images\\install.wim \
  --index 1 \
  --target D:\\
```

### Service an image with drivers, features, and updates
```bash
python -m better11.cli deploy service \
  --image C:\\images\\install.wim \
  --mount C:\\mounts\\install \
  --driver C:\\drivers\\lan.inf --driver C:\\drivers\\gpu\\ \
  --feature NetFx3 --feature Microsoft-Windows-Subsystem-Linux \
  --update C:\\updates\\kb5030269.cab
```

Deployment commands are Windows-only. On non-Windows hosts they will exit gracefully without performing actions.
