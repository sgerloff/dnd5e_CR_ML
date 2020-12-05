# dnd5e_CR_ML
This project serves as a testing bed to familiarize myself with some machine learning concepts. The goal is to develop a machine learning algorithm that can read the stat blocks of DnD 5e monsters and predict the challenge rating. One interesting usecase might be to identify the challenge rating of homebrewed monsters.


# Work in Progress:

## Data Inventory
The data from https://5e.tools/ contains 1365 monsters, with known CR, not legendary, not mythic and not copies of other monsters. The distribution of monsters per challenge rating is shown in the histogram:

![alt text](https://github.com/sgerloff/dnd5e_CR_ML/blob/master/data/cr_histogram.png)

The challenge rating takes values from 0 to 23 and for small values even includes fractions (1/8, 1/4, 1/2). Since we have a classification task, this does not matter too much.

## Logistic regression for 3 features (Sanity Check)
To get going, lets see if this task can be trivially solved by feeding three key numeric features: The sum of attributes, the number of skill proficiencies and the number of save proficiencies. Note: This should fail and give high bias, as even experienced humans should not be able to give the right call with this information.
The results is summarized in the following learning curve:

![alt text](https://github.com/sgerloff/dnd5e_CR_ML/blob/master/data/leaning_curve_logistic_regression.png)

We clearly see the expected high bias.

## Next step:
We have a high bias issue. Therefore we aim to add more features, such as the average hit points, action descriptions and more.
