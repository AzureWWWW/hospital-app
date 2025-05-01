import { Component } from '@angular/core';
import { UpdateDialogComponent } from "../components/update-dialog/update-dialog.component";

@Component({
  selector: 'app-home',
  imports: [UpdateDialogComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {

}
