# Adult Example

- [UCI Adult Data Set](https://archive.ics.uci.edu/ml/datasets/adult)

## Notes

- We downsample to 500 samples for baseline and 500 for test.
  We use a simple strategy of extracting 500-row blocks.
  No effort is made to control for proportions or representation.
- No feature rank information is available. We set rank equal to position of the field in the documented list of names.
