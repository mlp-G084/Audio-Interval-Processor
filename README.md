# Audio-Interval-Processor
To preprocess the polyphony audio labels or multitrack audio labels for model training. It can conduct intersection and exclusion on multiple audio tracks for multiple instruments.




Function 1: polyphonyByInstrument(file path, name of one instrument of interest, length of model input in seconds)
Gives the start time and end time of the polypony for a given instrument.


Function 2: total_count(length of model input in seconds)
Gives the calculated length of all the instruments in polyphony conditions.
