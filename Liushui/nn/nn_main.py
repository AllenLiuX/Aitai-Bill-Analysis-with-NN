import nn_pred as pred
import generator as generator
import time

raw_path = '../output/yikongall2.xlsx'
# input_path = 'xlsx_files/yikong_label.xlsx'
output_path = 'xlsx_files/yikong_predict2.xlsx'


def predict_all(raw_path, input_path, output_path):
    labeled_df = generator.main(raw_path, input_path, write_excel=False, show_plot=False)
    pred_df = pred.main(labeled_df, output_path, input_by_df=True, write_excel=False, show_plot=False)
    print(pred_df)


if __name__ == '__main__':
    start_time = time.time()
    predict_all(raw_path, '', output_path)
    end_time = time.time()
    print('======= Time taken: %f =======' %(end_time - start_time))