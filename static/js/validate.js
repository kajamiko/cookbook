      function validate()
      {
      
         if( document.reg_form.cookbook_name.value.length < 4 )
         {
            alert( "Title has to be longer than 4 characters!" );
            document.reg_form.cookbook_name.focus() ;
            return false;
         }

         if( document.reg_form.author_name.value.length < 4 )
         {
            alert( "Please provide your name!" );
            document.reg_form.author_name.focus() ;
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
         
        
      }