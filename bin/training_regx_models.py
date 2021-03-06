#!/usr/bin/env python

import pandas as pd
import argparse
import numpy as np
from sklearn import preprocessing

from regx_algorithms import AdaBoost
from regx_algorithms import Baggin
from regx_algorithms import DecisionTree
from regx_algorithms import Gradient
from regx_algorithms import knn_regression
from regx_algorithms.neural_network_regx import NeuralNetwork
from regx_algorithms import NuSVR
from regx_algorithms import RandomForest
from regx_algorithms import SVR
from regx_algorithms import performanceData
from class_algorithms import summaryStatistic
from tensorflow import keras
from joblib import dump, load
from os import path
import json


# funcion que permite calcular los estadisticos de un atributo en el set de datos, asociados a las medidas de desempeno
def estimated_statistic_performance(summary_obj, attribute):

    statistic = summary_obj.calculateValuesForColumn(attribute)
    row = [
        attribute,
        statistic["mean"],
        statistic["std"],
        statistic["var"],
        statistic["max"],
        statistic["min"],
    ]

    return row


def main():

    args = parse_arguments()

    encode = args.encoding
    dataset_training = pd.read_csv(args.input_1, index_col=0)
    dataset_testing = pd.read_csv(args.input_2, index_col=0)
    path_output = args.output

    # split into dataset and class
    response_training = dataset_training["response"]
    response_testing = dataset_testing["response"]

    matrix_dataset_training = dataset_training.drop("response", axis=1)
    matrix_dataset_testing = dataset_testing.drop("response", axis=1)

    # generamos una lista con los valores obtenidos...
    header = ["Algorithm", "Params", "R_Score", "Pearson", "Spearman", "Kendalltau"]
    matrixResponse = []

    regx_model_save = []

    # comenzamos con las ejecuciones...

    # AdaBoost
    for loss in ["linear", "squar", "exponential"]:
        for n_estimators in [10, 100, 1000]:
            try:
                print("Excec AdaBoostRegressor with ", loss, n_estimators)
                AdaBoostObject = AdaBoost.AdaBoost(
                    matrix_dataset_training, response_training, n_estimators, loss
                )
                AdaBoostObject.trainingMethod()

                # get predictions for get performance
                predictions_data = AdaBoostObject.model.predict(matrix_dataset_testing)
                performanceValues = performanceData.performancePrediction(
                    response_testing, predictions_data.tolist()
                )
                pearsonValue = performanceValues.calculatedPearson()["pearsonr"]
                spearmanValue = performanceValues.calculatedSpearman()["spearmanr"]
                kendalltauValue = performanceValues.calculatekendalltau()["kendalltau"]
                r_score_value = performanceValues.calculateR2_score()
                params = "loss:%s-n_estimators:%d" % (loss, n_estimators)
                row = [
                    "AdaBoostClassifier",
                    params,
                    r_score_value,
                    pearsonValue,
                    spearmanValue,
                    kendalltauValue,
                ]
                matrixResponse.append(row)
                regx_model_save.append(AdaBoostObject.model)

            except Exception as e:
                print("error ada", e)
                pass

    # Baggin
    for bootstrap in [True, False]:
        for n_estimators in [10, 100, 1000]:
            try:
                print("Excec Bagging with ", bootstrap, n_estimators)
                bagginObject = Baggin.Baggin(
                    matrix_dataset_training, response_training, n_estimators, bootstrap
                )
                bagginObject.trainingMethod()

                predictions_data = bagginObject.model.predict(matrix_dataset_testing)
                performanceValues = performanceData.performancePrediction(
                    response_testing, predictions_data.tolist()
                )
                pearsonValue = performanceValues.calculatedPearson()["pearsonr"]
                spearmanValue = performanceValues.calculatedSpearman()["spearmanr"]
                kendalltauValue = performanceValues.calculatekendalltau()["kendalltau"]
                r_score_value = performanceValues.calculateR2_score()
                params = "bootstrap:%s-n_estimators:%d" % (str(bootstrap), n_estimators)
                row = [
                    "Bagging",
                    params,
                    r_score_value,
                    pearsonValue,
                    spearmanValue,
                    kendalltauValue,
                ]
                print(row)
                matrixResponse.append(row)
                regx_model_save.append(bagginObject.model)

            except Exception as e:
                print("error baggin", e)
                pass

    # DecisionTree
    for criterion in ["mse", "friedman_mse", "mae"]:
        for splitter in ["best", "random"]:
            try:
                print("Excec DecisionTree with ", criterion, splitter)
                decisionTreeObject = DecisionTree.DecisionTree(
                    matrix_dataset_training, response_training, criterion, splitter
                )
                decisionTreeObject.trainingMethod()

                predictions_data = decisionTreeObject.model.predict(
                    matrix_dataset_testing
                )

                performanceValues = performanceData.performancePrediction(
                    response_testing, predictions_data.tolist()
                )
                pearsonValue = performanceValues.calculatedPearson()["pearsonr"]
                spearmanValue = performanceValues.calculatedSpearman()["spearmanr"]
                kendalltauValue = performanceValues.calculatekendalltau()["kendalltau"]
                r_score_value = performanceValues.calculateR2_score()

                print(predictions_data)
                print(response_testing)
                params = "criterion:%s-splitter:%s" % (criterion, splitter)
                row = [
                    "DecisionTree",
                    params,
                    r_score_value,
                    pearsonValue,
                    spearmanValue,
                    kendalltauValue,
                ]
                print(row)
                matrixResponse.append(row)
                regx_model_save.append(decisionTreeObject.model)

            except Exception as e:
                print("error tree", e)
                pass

    # gradiente
    for loss in ["ls", "lad", "huber", "quantile"]:
        for criterion in ["friedman_mse", "mse", "mae"]:
            for n_estimators in [10, 100, 1000]:
                try:
                    print(
                        "Excec GradientBoostingRegressor with ",
                        loss,
                        n_estimators,
                        2,
                        1,
                    )
                    gradientObject = Gradient.Gradient(
                        matrix_dataset_training,
                        response_training,
                        n_estimators,
                        loss,
                        criterion,
                        2,
                        1,
                    )
                    gradientObject.trainingMethod()

                    predictions_data = gradientObject.model.predict(
                        matrix_dataset_testing
                    )

                    performanceValues = performanceData.performancePrediction(
                        response_testing, predictions_data.tolist()
                    )
                    pearsonValue = performanceValues.calculatedPearson()["pearsonr"]
                    spearmanValue = performanceValues.calculatedSpearman()["spearmanr"]
                    kendalltauValue = performanceValues.calculatekendalltau()[
                        "kendalltau"
                    ]
                    r_score_value = performanceValues.calculateR2_score()

                    params = (
                        "criterion:%s-n_estimators:%d-loss:%s-min_samples_split:%d-min_samples_leaf:%d"
                        % (criterion, n_estimators, loss, 2, 1)
                    )
                    row = [
                        "GradientBoostingClassifier",
                        params,
                        r_score_value,
                        pearsonValue,
                        spearmanValue,
                        kendalltauValue,
                    ]
                    print(row)
                    matrixResponse.append(row)
                    regx_model_save.append(gradientObject.model)

                except Exception as e:
                    print("error gradiente", e)
                    pass

    # knn
    for n_neighbors in range(2, 11):
        for algorithm in ["auto", "ball_tree", "kd_tree", "brute"]:
            for metric in ["minkowski", "euclidean"]:
                for weights in ["uniform", "distance"]:
                    try:
                        print(
                            "Excec KNeighborsRegressor with ",
                            n_neighbors,
                            algorithm,
                            metric,
                            weights,
                        )
                        knnObect = knn_regression.KNN_Model(
                            matrix_dataset_training,
                            response_training,
                            n_neighbors,
                            algorithm,
                            metric,
                            weights,
                        )
                        knnObect.trainingMethod()

                        predictions_data = knnObect.model.predict(
                            matrix_dataset_testing
                        )

                        performanceValues = performanceData.performancePrediction(
                            response_testing, predictions_data.tolist()
                        )
                        pearsonValue = performanceValues.calculatedPearson()["pearsonr"]
                        spearmanValue = performanceValues.calculatedSpearman()[
                            "spearmanr"
                        ]
                        kendalltauValue = performanceValues.calculatekendalltau()[
                            "kendalltau"
                        ]
                        r_score_value = performanceValues.calculateR2_score()

                        params = "n_neighbors:%d-algorithm:%s-metric:%s-weights:%s" % (
                            n_neighbors,
                            algorithm,
                            metric,
                            weights,
                        )
                        row = [
                            "KNeighborsClassifier",
                            params,
                            r_score_value,
                            pearsonValue,
                            spearmanValue,
                            kendalltauValue,
                        ]
                        print(row)
                        matrixResponse.append(row)
                        regx_model_save.append(knnObect.model)

                    except Exception as e:
                        print("error knn", e)
                        pass

    # NuSVR
    for kernel in ["rbf", "linear", "poly", "sigmoid", "precomputed"]:
        for nu in [0.01, 0.05, 0.1]:
            for degree in range(3, 5):
                try:
                    print("Excec NuSVM")
                    nuSVM = NuSVR.NuSVRModel(
                        matrix_dataset_training,
                        response_training,
                        kernel,
                        degree,
                        0.01,
                        nu,
                    )
                    nuSVM.trainingMethod()
                    predictions_data = nuSVM.model.predict(matrix_dataset_testing)

                    performanceValues = performanceData.performancePrediction(
                        response_testing, predictions_data.tolist()
                    )
                    pearsonValue = performanceValues.calculatedPearson()["pearsonr"]
                    spearmanValue = performanceValues.calculatedSpearman()["spearmanr"]
                    kendalltauValue = performanceValues.calculatekendalltau()[
                        "kendalltau"
                    ]
                    r_score_value = performanceValues.calculateR2_score()

                    params = "kernel:%s-nu:%f-degree:%d-gamma:%f" % (
                        kernel,
                        nu,
                        degree,
                        0.01,
                    )
                    row = [
                        "NuSVM",
                        params,
                        r_score_value,
                        pearsonValue,
                        spearmanValue,
                        kendalltauValue,
                    ]
                    matrixResponse.append(row)
                    regx_model_save.append(nuSVM.model)

                except Exception as e:
                    print("error nusvr", e)
                    pass

    # SVC
    for kernel in ["rbf", "linear", "poly", "sigmoid", "precomputed"]:
        for degree in range(3, 5):
            try:
                print("Excec SVM")
                svm = SVR.SVRModel(
                    matrix_dataset_training, response_training, kernel, degree, 0.01
                )
                svm.trainingMethod()

                predictions_data = svm.model.predict(matrix_dataset_testing)

                performanceValues = performanceData.performancePrediction(
                    response_testing, predictions_data.tolist()
                )
                pearsonValue = performanceValues.calculatedPearson()["pearsonr"]
                spearmanValue = performanceValues.calculatedSpearman()["spearmanr"]
                kendalltauValue = performanceValues.calculatekendalltau()["kendalltau"]
                r_score_value = performanceValues.calculateR2_score()

                params = "kernel:%s-degree:%d-gamma:%f" % (kernel, degree, 0.01)
                row = [
                    "SVM",
                    params,
                    r_score_value,
                    pearsonValue,
                    spearmanValue,
                    kendalltauValue,
                ]
                matrixResponse.append(row)

                regx_model_save.append(svm.model)

            except Exception as e:
                print("error svc", e)
                pass

    # RF
    for n_estimators in [10, 100, 1000]:
        for criterion in ["mse", "mae"]:
            for bootstrap in [True, False]:
                try:
                    print("Excec RF")
                    rf = RandomForest.RandomForest(
                        matrix_dataset_training,
                        response_training,
                        n_estimators,
                        criterion,
                        2,
                        1,
                        bootstrap,
                    )
                    rf.trainingMethod()

                    predictions_data = rf.model.predict(matrix_dataset_testing)
                    performanceValues = performanceData.performancePrediction(
                        response_testing, predictions_data.tolist()
                    )
                    pearsonValue = performanceValues.calculatedPearson()["pearsonr"]
                    spearmanValue = performanceValues.calculatedSpearman()["spearmanr"]
                    kendalltauValue = performanceValues.calculatekendalltau()[
                        "kendalltau"
                    ]
                    r_score_value = performanceValues.calculateR2_score()

                    params = (
                        "n_estimators:%d-criterion:%s-min_samples_split:%d-min_samples_leaf:%d-bootstrap:%s"
                        % (n_estimators, criterion, 2, 1, str(bootstrap))
                    )
                    row = [
                        "RandomForestRegressor",
                        params,
                        r_score_value,
                        pearsonValue,
                        spearmanValue,
                        kendalltauValue,
                    ]
                    matrixResponse.append(row)
                    print(row)
                    regx_model_save.append(rf.model)

                except Exception as e:
                    print("error rf", e)
                    pass

    for n_layers in [1, 2]:
        for n_neurons in [64, 128, 256]:
            for activation in ["relu", "sigmoid"]:
                try:
                    n_features = len(matrix_dataset_training.columns)
                    nn_model = NeuralNetwork(
                        n_features, n_neurons, n_layers, activation=activation
                    )
                    nn_model.train_model(matrix_dataset_training, response_training)

                    predictions = nn_model.predict(matrix_dataset_testing)
                    performanceValues = performanceData.performancePrediction(
                        response_testing.to_numpy(), predictions
                    )

                    pearsonValue = performanceValues.calculatedPearson()["pearsonr"]
                    spearmanValue = performanceValues.calculatedSpearman()["spearmanr"]
                    kendalltauValue = performanceValues.calculatekendalltau()[
                        "kendalltau"
                    ]
                    r_score_value = performanceValues.calculateR2_score()

                    params = f"Params"

                    row = [
                        "Fully connected neural network",
                        params,
                        r_score_value,
                        pearsonValue,
                        spearmanValue,
                        kendalltauValue,
                    ]

                    matrixResponse.append(row)
                    regx_model_save.append(nn_model)

                except Exception as e:
                    print("Error nn ", e)

    matrixResponseRemove = []
    for element in matrixResponse:
        if "ERROR" not in element:
            matrixResponseRemove.append(element)

    # generamos el export de la matriz convirtiendo a data frame
    dataFrameResponse = pd.DataFrame(matrixResponseRemove, columns=header)

    # generamos el nombre del archivo
    nameFileExport = path.join(path_output, f"{encode}_summaryProcessJob.csv")
    dataFrameResponse.to_csv(nameFileExport, index=False)

    # estimamos los estadisticos resumenes para cada columna en el header
    # instanciamos el object
    statisticObject = summaryStatistic.createStatisticSummary(nameFileExport)
    matrixSummaryStatistic = [
        estimated_statistic_performance(statisticObject, "R_Score"),
        estimated_statistic_performance(statisticObject, "Pearson"),
        estimated_statistic_performance(statisticObject, "Spearman"),
        estimated_statistic_performance(statisticObject, "Kendalltau"),
    ]

    # generamos el nombre del archivo
    dataFrame = pd.DataFrame(
        matrixSummaryStatistic,
        columns=["Performance", "Mean", "STD", "Variance", "MAX", "MIN"],
    )
    nameFileExport = path.join(path_output, f"{encode}_statisticPerformance.csv")
    dataFrame.to_csv(nameFileExport, index=False)

    dict_summary_meta_model = {}

    print("Process extract models")

    # get max value for each performance
    for i in range(len(dataFrame)):

        max_value = dataFrame["MAX"][i]
        performance = dataFrame["Performance"][i]

        print("MAX ", max_value, "Performance: ", performance)
        information_model = {}

        information_model.update({"Performance": performance})
        information_model.update({"Value": max_value})

        # search performance in matrix data and get position
        information_matrix = []
        model_matrix = []
        algorithm_data = []

        for j in range(len(dataFrameResponse)):
            difference_performance = abs(max_value - dataFrameResponse[performance][j])
            if difference_performance <= 0.000001:
                model_matrix.append(regx_model_save[j])
                algorithm_data.append(dataFrameResponse["Algorithm"][j])
                information_matrix.append(dataFrameResponse["Params"][j])

        array_summary = []

        for j in range(len(information_matrix)):
            model_data = {
                "algorithm": algorithm_data[j],
                "params": information_matrix[j],
            }
            array_summary.append(model_data)

        information_model.update({"models": array_summary})

        # export models
        for j, model in enumerate(model_matrix):
            if type(model) == NeuralNetwork:
                # Tensorflow cannot be pickled
                save_path = path.join(
                    path_output, f"{encode}_{performance}_model{str(j)}"
                )
                model.save_model(save_path, overwrite=True)

            else:
                save_path = path.join(
                    path_output, f"{encode}_{performance}_model{str(j)}.joblib"
                )
                dump(model, save_path)

        dict_summary_meta_model.update({performance: information_model})

    # export summary JSON file
    print("Export summary into JSON file")
    with open(path.join(path_output, f"{encode}_summary_meta_models.json"), "w") as fp:
        json.dump(dict_summary_meta_model, fp)


def parse_arguments():
    """
    Parse input arguments of script

    @return: arguments parser
    """

    parser = argparse.ArgumentParser(
        "Explore multiple regression algorithms using training and testing dataset provided as inputs"
    )

    parser.add_argument(
        "-i1",
        "--input-1",
        action="store",
        required=True,
        help="training dataset file in format csv",
    )

    parser.add_argument(
        "-i2",
        "--input-2",
        action="store",
        required=True,
        help="testing dataset file in format csv",
    )

    parser.add_argument(
        "-e",
        "--encoding",
        action="store",
        required=True,
        help="encoding used on the input dataset",
    )

    parser.add_argument(
        "-o",
        "--output",
        action="store",
        required=True,
        help="output path",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
