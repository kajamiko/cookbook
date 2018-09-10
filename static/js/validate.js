      function validate()
      {
      
         if( document.reg_form.cookbook_name.value.length < 4 )
         {
            alert( "Title has to be longer than 4 characters!" );
            document.reg_form.cookbook_name.focus() ;
            return false;
         }
         
          if( document.reg_form.author_name.value.length < 3 )
         {
            alert( "That's a name that will be displayed under all of your recipes...make it longer than 3 characters!" );
            document.reg_form.authorname.focus() ;
            return false;
         }
         
          if( document.reg_form.password.value.length < 5 )
         {
            alert( "Please provide at least 5 characters long password!" );
            document.reg_form.password.focus() ;
            return false;
         }
         
         if( document.reg_form.password.value !=  document.reg_form.con_password.value)
         {
            alert( "Passwords are not the same!" );
            return false;
         }
         return( true );
      }
      
      function validate_empty(){
         
         if( document.add_form.recipe_name.value.length < 4 )
         {
            alert( "Title has to be longer than 4 characters!" );
            document.add_form.cookbook_name.focus() ;
            return false;
         }
         
         if( document.add_form.recipe_name.files.files.length === 0 )
         {
            alert( "Did you forget about an image?" );
            document.add_form.cookbook_name.focus() ;
            return false;
         }
         if( document.add_form.cooking_time.value == "")
         {
            alert( "Please provide cooking time" );
            document.add_form.cooking_time.focus() ;
            return false;
         }
         
         if( document.add_form.servings.value == "")
         {
            alert( "Please provide, how many servings is your recipe for." );
            return false;
         }
         if( document.add_form.difficulty.value == "")
         {
            alert( "Please choose difficulty level." );
            return false;
         }
         
         if( document.add_form.dish_type.value == "")
         {
            alert( "Please choose dish_type." );
            return false;
         }
         
          if( document.add_form.ingredients_list.value.length < 10 )
         {
            alert( "Please provide a list of ingredients!" );
            document.add_form.ingredients_list.focus() ;
            return false;
         }
         
         if( document.add_form.preparation_steps_list.value.length < 10 )
         {
            alert( "Please share with others, how to prepare your dish!" );
            document.add_form.preparation_steps_list.focus() ;
            return false;
         }
         
        return( true );
      }
      
