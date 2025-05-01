import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ConfigService } from '../../services/config.service';
@Component({
  selector: 'app-new-appointment',
  imports: [FormsModule, CommonModule],
  templateUrl: './new-appointment.component.html',
  styleUrl: './new-appointment.component.css'
})
export class NewAppointmentComponent {
  configService = inject(ConfigService);
  specialtyList: any [] = [];
  selectedSpecialty: string = '';
  doctorsAvailable: any [] = [];
  clickedCheck: boolean = false;

  router = inject(Router);

  checkForm: any = {
      "specialty": "",
      "date": ""
  }
  createForm: any = {
    "doctor_name": "",
    "date": "",
    "time_slot": 0,
    "description": ""
  }

  getSpecialty() {
    this.configService.getAllSpecialty().subscribe((res: any) => {
      this.specialtyList = res;
    }, (error: any) => {
      alert(error.error.detail);
      console.error('Error Fetching Data:', error);
    });
  }

  getAvailableAppointment(){
    if (this.checkForm.specialty != "" , this.checkForm.date != ""){
      this.configService.getAvailableAppointment(this.checkForm).subscribe((res: any) => {
        this.doctorsAvailable = res.details;
        this.clickedCheck = true;
      }, (error: any) => {
        alert(error.error.detail);
        console.error('Error Fetching Data:', error);
      });
    } else {
      alert("Select specialty and date")
    }
  }

  ngOnInit(): void {
    this.getSpecialty();
  }

  onCreate(){
    if (this.createForm.doctor_name != "", this.createForm.time_slot != 0){

      this.configService.patientCreateAppointment(this.createForm).subscribe((res: any) => {
        alert(res.message)
      this.getAvailableAppointment()
      this.router.navigateByUrl("/home");
     }, (error: any) => {
       alert(error.error.detail);
       console.error('Error Fetching Data:', error);
     });
    } else {
      alert("Select one doctor and suitable time slot")
    }
  }
}
