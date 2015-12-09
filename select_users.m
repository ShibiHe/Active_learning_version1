clear;
load 'step2.mat';
N_user = size(train_rating,1);
M_train = size(train_rating,2);
M_test = size(predict_rating,2);

UI_matrix = train_rating;
for i = 1:N_user
    UI_matrix(i,:) = train_rating(i,:)/norm(train_rating(i,:));
    % some user did not have rating for these movies
    if norm(train_rating(i,:)) == 0
        UI_matrix(i,:) = 0;
    end
end
UU_similarity = UI_matrix*UI_matrix';
sum_U = sum(UU_similarity);


H=4*UU_similarity;
f=-sum_U';
Aeq=ones(1,N_user);
beq=0.1*N_user;
lb=zeros(N_user,1);
ub=ones(N_user,1);
[x,value]=quadprog(H,f,[],[],Aeq,beq,lb,ub);
[a,b]=sort(x,'descend');

%%
clear;
load 'step2.mat';
N_user = size(train_rating,1);
M_train = size(train_rating,2);
M_test = size(predict_rating,2);

UI_matrix = train_rating;
for i = 1:N_user
    UI_matrix(i,:) = train_rating(i,:)/norm(train_rating(i,:));
    % some user did not have rating for these movies
    if norm(train_rating(i,:)) == 0
        UI_matrix(i,:) = 0;
    end
end
UU_similarity = UI_matrix*UI_matrix';
sum_U = sum(UU_similarity);


% the final active learning choice:
ans_choosing_user_movie=zeros(N_user, M_test); 
% active learning users for one movie:
active_users_for_one_movie = int32(N_user*0.1)-1;
% every movie has positive movies:
alternative_users_for_one_movie = sum(positive_rating);

already_chose = zeros(1,M_test);
already_chose = logical(already_chose);
while sum(alternative_users_for_one_movie<active_users_for_one_movie)>0
    % slice chooses movies whose positive users are not enough
    slice=alternative_users_for_one_movie<active_users_for_one_movie;
    % for these movies just use positive users 
    ans_choosing_user_movie(:,slice)=positive_rating(:,slice);
    already_chose(slice)=true;
    cost_choices = sum(alternative_users_for_one_movie(slice));
    cost_movies = sum(slice);
    alternative_users_for_one_movie(slice) = inf;
    active_users_for_one_movie = int32((0.1*N_user-1)*M_test-cost_choices)/(M_test-cost_movies);
end

% already_chose
for movie = 1:M_test:
    if already_chose()