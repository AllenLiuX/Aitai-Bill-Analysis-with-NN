import nn_pred as pred
import generator as generator
import time

# raw_path = '../output/yikongall2.xlsx'
raw_path = 'xlsx_files/test2018.xlsx'
# input_path = 'xlsx_files/yikong_label.xlsx'
output_path = 'xlsx_files/test2018-pred.xlsx'


def predict_all(raw_path, input_path, output_path):
    labeled_df = generator.main(raw_path, input_path, write_excel=True, show_plot=False)
    pred_df = pred.main(labeled_df, output_path, input_by_df=True, write_excel=True, show_plot=False)
    print(pred_df)


if __name__ == '__main__':
    start_time = time.time()
    predict_all(raw_path, 'xlsx_files/temp.xlsx', output_path)
    end_time = time.time()
    print('======= Time taken: %f =======' %(end_time - start_time))