__author__ = 'frankhe'
TRUE_POSITIVE_SELECTOR = 0.5


def compute_classification(number_of_positive_data=None):
    if __name__ == '__main__':
        f1 = open('test_step1.libfm')
    else:
        f1 = open('Generate/test_step1.libfm')
        
    if __name__ == '__main__':
        f2 = open('prediction')
    else:
        f2 = open('Generate/prediction')

    test_data = f1.readlines()
    if number_of_positive_data is None:
        number_of_positive_data = len(test_data)
    prediction_data = f2.readlines()
    selected_data = []

    def f(x):
        if x > TRUE_POSITIVE_SELECTOR:
            return 1
        else:
            return 0

    tp = fp = tn = fn = positive = 0
    for i in range(len(test_data)):
        test_value = f(float(test_data[i].split()[0]))
        pred_value = f(float(prediction_data[i].strip()))
        if test_value == pred_value == 1:
            tp += 1
        if pred_value == 1 and test_value == 0:
            fp += 1
        if pred_value == 0 and test_value == 1:
            fn += 1
        if pred_value == test_value == 0:
            tn += 1
        if pred_value == 1:
            positive += 1
            selected_data.append(i)

    print 'number of test data=', len(test_data)
    print 'tp={0} fp={1} fn={2} tn={3}'.format(tp, fp, fn, tn)
    print 'precision={0} recall={1} positive={2}'.format(float(tp)/(tp+fp), float(tp)/(tp+fn), positive)

    tp = fp = tn = fn = positive = 0
    for i in range(number_of_positive_data):
        test_value = f(float(test_data[i].split()[0]))
        pred_value = f(float(prediction_data[i].strip()))
        if test_value == pred_value == 1:
            tp += 1
        if pred_value == 1 and test_value == 0:
            fp += 1
        if pred_value == 0 and test_value == 1:
            fn += 1
        if pred_value == test_value == 0:
            tn += 1
        if pred_value == 1:
            positive += 1
            selected_data.append(i)

    print 'number of positive test data=', number_of_positive_data
    print 'tp={0} fp={1} fn={2} tn={3}'.format(tp, fp, fn, tn)
    print 'precision={0} recall={1} positive={2}'.format(float(tp)/(tp+fp), float(tp)/(tp+fn), positive)

    return selected_data

if __name__ == '__main__':
    compute_classification()
