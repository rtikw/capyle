#!/bin/sh

echo "Start"

step=0.1

for x in $(seq -0.5 $step 0.5); do
  for y in $(seq -0.5 $step 0.5); do
    command="./run_with_custom_wind.sh "$x" "$y
    output=$($command)
    fire_at=$(echo $output | cut -d "[" -f2 | cut -d "]" -f1)
    echo -e "Wind X: "$x",\t Wind Y: "$y",\t Fire at: "$fire_at
  done
done

echo "End"

