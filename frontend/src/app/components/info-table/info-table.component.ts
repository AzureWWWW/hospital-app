import { Component , OnInit, inject, Input} from '@angular/core';

import {MatTableModule} from '@angular/material/table';
import {CommonModule } from '@angular/common';
import {FormsModule} from '@angular/forms';
import {MatIconModule} from '@angular/material/icon';
import {MatDialogModule } from '@angular/material/dialog';
import { AssignUserDialogComponent } from '../view_admin/assign-user-dialog/assign-user-dialog.component';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { ConfigService } from '../../services/config.service';
import { ComponentRegistryService } from '../../services/component-registry.service';


@Component({
  selector: 'app-info-table',
  standalone: true,
  imports: [CommonModule , MatTableModule,
    FormsModule, MatIconModule, MatDialogModule],
  templateUrl: './info-table.component.html',
  styleUrl: './info-table.component.css'

})

export class InfoTableComponent implements OnInit {
  constructor(public dialog: MatDialog, private registry: ComponentRegistryService) {}
  configService = inject(ConfigService);
  router = inject(Router);

  @Input() columns: string[] = [];
  @Input() dataSource: any[] = [];
  @Input() title: string = '';
  @Input() cpt!: any;
  @Input() id_name: string = '';
  @Input() func_call: any;


  _filterText: string = '';
  filteredData: any[] = [];
  isCollapsed: Boolean = false;
  ngOnInit():void{
    this.filteredData = [...this.dataSource];
  }

  // getter and setter for the text the user is entering within the filtering box
  get filterText(){
    return this._filterText;
  }
  set filterText(value: string){
    this._filterText = value;
  }

  collapseView(){
    this.isCollapsed = true;
  }
  maximizeView(){
    this.isCollapsed = false;
  }

  // filter data based on the entered filter text
  filterData(){
    const term = this.filterText.trim().toLowerCase();
    if (!term) {
      this.filteredData = [...this.dataSource];
      return;
    }
    this.filteredData = this.dataSource.filter(app =>
      this.columns.some(col =>
        String(app[col])?.toLowerCase().includes(term)
      )
    );
  }
  assignUser(){
    if (this.title =="appointments"){
      this.router.navigateByUrl("/new_appointment");
    }
    else{
      const dialogRef = this.dialog.open(AssignUserDialogComponent, {
        data: {
          title: this.title,
        },
        width: '300px',
        height: '350px',
      });
      dialogRef.afterClosed().subscribe(result => {
        if (this.func_call) {
          this.func_call.subscribe(
            (response:any) => {
              this.dataSource = response;
              this.filteredData = response;

            },
            (error:any) => {
              console.error('Error fetching data:', error);
            }
          );
        }

        }
      );
    }

  }

  updateDialog(element: any){
    let element_id = element[this.id_name];


    const component = this.registry.getComponent(this.cpt);
    console.log(component)
    if (!component || this.id_name === undefined) {
      console.warn(`Dialog component or ID is missing for"${this.cpt}"`);
      return;
    }

    // open dialog
    const dialogRef = this.dialog.open(component , {
      data: {
        id: element_id,
        title: this.title,
        func_call: this.func_call,
        id_name: this.id_name,
      },
      width: '500px',
      height: '550px',
    });

    // update results view after the dialog being closed
    dialogRef.afterClosed().subscribe(result => {
      if (this.func_call) {
        this.func_call.subscribe(
          (response:any) => {
            this.dataSource = response;
            this.filteredData = response;
          },
          (error:any) => {
            alert(error.error.detail);
            console.error('Error fetching data:', error);
          }
        );
      }

    });
  }

  }

