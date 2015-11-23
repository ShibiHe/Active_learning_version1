__author__ = 'frankhe'


def computer_error():
    if __name__ == '__main__':
        f1 = open('test_step3.libfm')
    else:
        f1 = open('Generate/test_step3.libfm')

    if __name__ == '__main__':
        f2 = open('prediction')
    else:
        f2 = open('Generate/prediction')

    test_data = f1.readlines()
    prediction_data = f2.readlines()

    total_abs_error = total_square_error = 0
    max_abs_error = 0

    for i in range(len(test_data)):
        test_value = float(test_data[i].split()[0])
        pred_value = float(prediction_data[i].strip())
        error = abs(test_value-pred_value)
        if error>max_abs_error:
            max_abs_error = error
        total_abs_error += error
        total_square_error += error*error

    print 'number of test data=', len(test_data)
    print 'prediction score is float'
    print 'total abs error=', total_abs_error, '\navg abs error=', total_abs_error/len(test_data)
    print 'total square error=', total_square_error, '\navg square error=', total_square_error/len(test_data)
    print 'max abs error=', max_abs_error

    total_abs_error = total_square_error = 0
    max_abs_error = 0

    for i in range(len(test_data)):
        test_value = float(round(float(test_data[i].split()[0])))
        pred_value = float(round(float(prediction_data[i].strip())))
        error = abs(test_value-pred_value)
        if error>max_abs_error:
            max_abs_error = error
        total_abs_error += error
        total_square_error += error*error

    print '\nprediction score is rounded'
    print 'total abs error=', total_abs_error, '\navg abs error=', total_abs_error/len(test_data)
    print 'total square error=', total_square_error, '\navg square error=', total_square_error/len(test_data)
    print 'max abs error=', max_abs_error

if __name__ == '__main__':
    computer_error()