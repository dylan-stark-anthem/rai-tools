all: adult.csv adult_baseline.csv adult_test.csv

clean:
	rm adult.csv adult_baseline.csv adult_test.csv

adult.csv:
	curl https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data > adult.csv
	sed -i 's/,[^,]*$$//' adult.csv

adult_baseline.csv: adult.csv
	echo "age,workclass,fnlwgt,education,educational-num,marital-status,occupation,relationship,race,gender,capital-gain,capital-loss,hours-per-week,native-country" > adult_baseline.csv
	head -n 500 adult.csv >> adult_baseline.csv

adult_test.csv: adult.csv
	echo "age,workclass,fnlwgt,education,educational-num,marital-status,occupation,relationship,race,gender,capital-gain,capital-loss,hours-per-week,native-country" > adult_test.csv
	tail -n 501 adult.csv >> adult_test.csv

.PHONY: all
