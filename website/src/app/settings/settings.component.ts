import { Component, OnInit } from '@angular/core';
import { ActionSheetController, AlertController, Platform } from 'ionic-angular';
import { TranslateService } from '@ngx-translate/core';
import { I18nService } from '@app/core/i18n.service';
import { AuthenticationService } from '@app/core/authentication/authentication.service';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService } from '../core/api/ApiService';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss']
})
export class SettingsComponent implements OnInit {
  private list: any[] = [];
  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.getFaces();
  }

  getFaces() {
    let that = this;
    this.apiService.getFaces().subscribe((data: any) => {
      console.log(data);
      that.list = data;
    });
  }

  deleteFace(face: any, index: number): void {
    let that = this;
    this.apiService.deleteFace(face.faceId).subscribe((data: any) => {
      that.list.splice(index, 1);
    });
  }
}
