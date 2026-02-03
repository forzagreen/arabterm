import { Component } from '@angular/core';
import { Dictionary, dictionaries } from '../dictionaries';


@Component({
  selector: 'app-dictionary-list',
  standalone: false,
  templateUrl: './dictionary-list.component.html',
  styleUrls: ['./dictionary-list.component.css']
})
export class DictionaryListComponent {
  constructor() {}

  dictionaries: Dictionary[] = dictionaries;
}
