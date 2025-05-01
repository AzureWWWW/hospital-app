import { Injectable } from '@angular/core';
import { HttpClient, HttpParams} from '@angular/common/http';
import { Observable } from 'rxjs';
import { Appointment } from '../models/appointment';
import { Patient } from '../models/patient';
import { Doctor } from '../models/doctor';
import { User } from '../models/user';
import { Admin } from '../models/admin';


// to inject services on other places
@Injectable({
  providedIn: 'root'
})

export class ConfigService {

  private config: any;

  token = localStorage.getItem("token");

  constructor(private http: HttpClient){
    this.config = {
      "base_url": "https://localhost:8432/",
    };
  }

  // get the base Url
  getBaseUrl(): String{
    return this.config.base_url
  }

  getUserRole(): Observable<any>{
    const user_url =this.config.base_url+ 'users/getUserRole/';
    return this.http.get(user_url);
  }

  // ****************** Admin View ******************

  // get all appointments history
  getAppointmentData(): Observable<any>{
    const appointment_url = this.config.base_url + "appointments/getAllAppointments";
    return this.http.get(appointment_url);
  }

  // update an appointment
  admin_update_appointmentData(id: number, updatedAppointment: Appointment): Observable<any>{
    const appointment_url = `${this.config.base_url}appointments/adminUpdateAppointment/${id}`;
    return this.http.put(appointment_url, updatedAppointment);
  }

  // get all patients history
  getPatientData(): Observable<any>{
    const patient_url = this.config.base_url + "patients/getAllPatients";
    return this.http.get(patient_url);
  }

  // update patient's status expiry
  update_patient_status_expiry(patient_id: number, updatedPatient: Patient): Observable<any>{
    const patient_url = `${this.config.base_url}patients/update_patient_status_expiry/?patient_id=${patient_id}`;
    return this.http.put(patient_url, updatedPatient, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.token}`
      }
    });
  }
  // get all patients history
  getDoctorData(): Observable<any>{
    const doctor_url = this.config.base_url + "doctors/getAllDoctors";
    return this.http.get(doctor_url);
  }

  // update doctor's status expiry
  update_doctor_status_expiry(doctor_id: number, updatedDoctor: Doctor): Observable<any>{
    const doctor_url = `${this.config.base_url}doctors/update_doctor_status_expiry/?doctor_id=${doctor_id}`;
    return this.http.put(doctor_url, updatedDoctor);
  }

  getNonAssignedUsers(){
    const admin_url = this.config.base_url + "admins/getNonAssignedUsers";
    return this.http.get(admin_url);
  }
  isDefaultAdmin(): Observable<any>{
    const admin_url = this.config.base_url + "admins/isDefaultAdmin";
    return this.http.get(admin_url);
  }
  updateRole(user_id: number, updatedUser:any){
    const admin_url = `${this.config.base_url}admins/updateRole/${user_id}`;
    return this.http.put(admin_url, updatedUser);
  }
  getAdminData(): Observable<any>{
    const admin_url = this.config.base_url + "admins/getAllAdmins";
    return this.http.get(admin_url);
  }
  // update doctor's status expiry
  update_admin_status_expiry(admin_id: number, updatedAdmin: Admin): Observable<any>{
      const admin_url = `${this.config.base_url}admins/update_admin_status_expiry/?admin_id=${admin_id}`;
      return this.http.put(admin_url, updatedAdmin);
  }

  // ****************** Doctor View & Patient View ******************

  // get a doctor appointments
  getDoctorAppointments(): Observable<any>{
    // We are passing the doctor_id
    const doctor_url = this.config.base_url+ 'appointments/getDoctorAppointments/';
    return this.http.get(doctor_url);
  }
  // get a patient appointments
  getPatientAppointments(): Observable<any>{
    // We are passing the patient_id
    const doctor_url = this.config.base_url + 'appointments/getPatientAppointments/';
    return this.http.get(doctor_url);
  }

  // update an appointment
  user_update_appointmentData(id: number, updatedAppointment: Appointment): Observable<any>{
    const appointment_url = `${this.config.base_url}appointments/userUpdateAppointment/${id}`;
    return this.http.put(appointment_url, updatedAppointment);
  }
  getUserInfo(): Observable<any>{
    const user_url = this.config.base_url +'users/getUserInfo/';
    return this.http.get(user_url);
  }
  update_my_profile(updatedProfile: Doctor):Observable<any>{
    const user_url = this.config.base_url + "users/updateMyProfile/";
    return this.http.put(user_url, updatedProfile);
  }
  getAvailableAppointmentByAppointmentId(appointment_id: number, date: string): Observable<any>{
    const user_url = this.config.base_url +'appointments/getAvailableAppointmentByAppointmentId/';
    const params = new HttpParams()
      .set('appointment_id', appointment_id.toString())
      .set('date', date);
    return this.http.get(user_url, { params });
  }
  logOut():Observable<any>{
    const user_url = this.config.base_url + "auth/logout/";
    return this.http.post(user_url,{});
  }

  patientCreateAppointment(form: any):Observable<any>{
    const user_url = this.config.base_url + "appointments/PatientCreateAppointment/";
    return this.http.post(user_url,form);
  }
  getAvailableAppointment(form: any):Observable<any>{
    const user_url = this.config.base_url + "appointments/getAvailableAppointment/";
    return this.http.post(user_url,form);
  }
  getAllSpecialty():Observable<any>{
    const user_url = this.config.base_url + "doctors/getAllSpecialty/";
    return this.http.get(user_url);
  }
  register(form: any):Observable<any>{
    const user_url = this.config.base_url + "auth/register/";
    return this.http.post(user_url,form);
  }
  login(body: any, header: any):Observable<any>{
    const user_url = this.config.base_url + "auth/login/";
    return this.http.post(user_url,body, { headers: header });
  }
  setTokenToExpired(token: string):Observable<any>{
    const user_url = `${this.config.base_url}auth/setTokenToExpired/?token=${token}`;
    return this.http.post(user_url, {});
  }

}
