#!/usr/bin/env fish

# must be run in project root
# resizes all images in web/images/png/fnf-full/
# saving them to web/images/cards/{medium,large,small,full} as jpg
# requires `convert` from ImageMagick

if not which convert >/dev/null
  echo "ImageMagick's 'convert' command not found. Please install ImageMagick."
  exit 1
end

if not test -d web/images/png/fnf-full || not test -d web/images/cards/small || not test -d web/images/cards/medium || not test -d web/images/cards/large || not test -d web/images/cards/full
  echo "make sure that these directories exist: web/images/cards/{medium,large,small,full}"
  echo "run this script from the project root"
  echo "ex: fish ./bin/resize-fnf-pngs.fish"
  exit 1
end

for file in (ls web/images/png/fnf-full)
  set name (string split -m1 -r '.' $file)[1]
    convert web/images/png/fnf-full/$file web/images/cards/full/$name.jpg
    convert -resize 300x419 web/images/png/fnf-full/$file web/images/cards/large/$name.jpg
    convert -resize 165x230 web/images/png/fnf-full/$file web/images/cards/medium/$name.jpg
    convert -resize 116x162 web/images/png/fnf-full/$file web/images/cards/small/$name.jpg
end
