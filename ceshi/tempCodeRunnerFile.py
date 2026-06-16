% 性别分布  
gender_labels = {'男', '女', '不愿意透露'};  
gender_values = [45, 50, 5];  

% 年级分布  
grade_labels = {'大一', '大二', '大三', '大四', '研究生及以上'};  
grade_values = [30, 25, 20, 15, 10];  

% 每天吃早餐情况  
breakfast_labels = {'是', '否', '视情况而定'};  
breakfast_values = [60, 10, 30];  

% 吃早餐时间  
breakfast_time_labels = {'6:00-7:00', '7:00-8:00', '8:00-9:00', '9:00以后'};  
breakfast_time_values = [10, 40, 35, 15];  

% 吃早餐地点  
breakfast_location_labels = {'宿舍/家里', '学校食堂', '校外餐馆/小吃店', '路边摊/快餐店', '其他'};  
breakfast_location_values = [20, 50, 15, 10, 5];  

% 早餐选择  
breakfast_choice_labels = {'主食类', '饮品类', '果蔬类', '蛋类', '肉类', '其他'};  
breakfast_choice_values = [80, 70, 40, 50, 30, 20];  

% 不吃早餐的原因  
no_breakfast_reason_labels = {'时间不够', '不饿', '认为不吃没关系', '控制体重', '经济原因', '其他'};  
no_breakfast_reason_values = [60, 30, 20, 25, 10, 5];  

% 对学校提供的帮助需求  
help_needs_labels = {'提供更丰富的早餐选择', '提供更早的早餐时间', '开展营养教育活动', '提供经济补贴或优惠', '其他'};  
help_needs_values = [70, 40, 60, 50, 10];  

% 对学校早餐服务满意度  
satisfaction_labels = {'非常满意', '满意', '一般', '不满意', '非常不满意'};  
satisfaction_values = [10, 30, 40, 15, 5];  

% 创建一个图形窗口  
figure;  

% 性别分布饼图  
subplot(3, 2, 1);  
pie(gender_values, gender_labels);  
title('性别分布');  

% 年级分布柱状图  
subplot(3, 2, 2);  
bar(grade_values, 'FaceColor', [0.2, 0.6, 0.8]);  
set(gca, 'XTickLabel', grade_labels);  
title('年级分布');  
ylabel('百分比 (%)');  

% 早餐情况饼图  
subplot(3, 2, 3);  
pie(breakfast_values, breakfast_labels);  
title('是否每天吃早餐');  

% 早餐时间柱状图  
subplot(3, 2, 4);  
bar(breakfast_time_values, 'FaceColor', [0.8, 0.4, 0.2]);  
set(gca, 'XTickLabel', breakfast_time_labels);  
title('吃早餐的时间');  
ylabel('百分比 (%)');  

% 早餐地点饼图  
subplot(3, 2, 5);  
pie(breakfast_location_values, breakfast_location_labels);  
title('吃早餐地点');  

% 早餐选择柱状图  
subplot(3, 2, 6);  
bar(breakfast_choice_values, 'FaceColor', [0.4, 0.8, 0.4]);  
set(gca, 'XTickLabel', breakfast_choice_labels);  
title('早餐选择');  
ylabel('百分比 (%)');  

% 调整图形布局  
sgtitle('早餐调查数据分析');