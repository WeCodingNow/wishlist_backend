def jsoner(vk_id = None,**kwargs):
    
    response={'status':kwargs['status']}
    if kwargs['status'] == 400:
        response['text']='Bad Request'
    elif kwargs['status'] == 403:
        response['text']='Forbidden'
    else:
        response['text']='OK'
        if 'wishlist' in kwargs.keys():
            wishlist = kwargs['wishlist']
            # print(kwargs['wishlist'])
            for wish in wishlist:
                if wish['gift'] == vk_id:
                    wish['gift'] = 'You'
                elif wish['gift'] == None:
                    wish['gift'] = 'Nobody'
                else:
                    wish['gift'] = 'Somebody'
            response['products'] = wishlist
        elif 'searchlist' in kwargs.keys():
            response['products'] = kwargs['searchlist']
        elif 'user_giftlist' in kwargs.keys():
            response['products'] = kwargs['user_giftlist']
        elif 'giftlist' in kwargs.keys():
            wishlist = kwargs['giftlist']
            users=[]
            for user, products in wishlist.items():
                user = {'vk_id':user,'products':products}
                users.append(user)
            response['users']=users
        elif 'token' in kwargs.keys():
            response['token']=kwargs['token']

    return response