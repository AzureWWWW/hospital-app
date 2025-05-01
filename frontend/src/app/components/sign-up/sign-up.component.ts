import { CommonModule } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { error } from 'console';
import { ConfigService } from '../../services/config.service';

@Component({
  selector: 'app-sign-up',
  imports: [FormsModule, CommonModule],
  templateUrl: './sign-up.component.html',
  styleUrl: './sign-up.component.css'
})
export class SignUpComponent{
  configService = inject(ConfigService);
  // http = inject(HttpClient);
  router = inject(Router);

  registerForm: any = {
    "username": "",
    "first_name": "",
    "last_name": "",
    "email": "",
    "phone_number": "",
    "password": ""
  }

  onSignUp(){
    debugger;
    const formValue = this.registerForm;
    // this.http.post("http://127.0.0.1:8000/auth/register/", formValue)
    this.configService.register(formValue).subscribe((res:any)=>{
      alert(res.message)
      this.router.navigateByUrl("login")
    }, (error: HttpErrorResponse)=>{
      console.error(error);
      if (error.error && error.error.detail) {
        alert(`Signup failed: ${error.error.detail}`);
      } else {
        alert("Signup failed: An unexpected error occurred.");
      }
    })
  }

}
