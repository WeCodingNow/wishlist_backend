create table Users (user_id serial primary key , vk_id text unique);

create table Wish (wish_id serial primary key , user_id int references Users(user_id), product_id text, gift_id text);
