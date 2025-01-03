import {Component, OnInit} from '@angular/core';
import {Link} from "../../domains/Link";
import {ActivatedRoute, Router} from "@angular/router";
import {NavigationService} from "../../services/navigation.service";
import {Case} from "../../domains/Case";
import {AetherOneService} from "../../services/aether-one.service";
import {FormControl} from "@angular/forms";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  serverOnline:boolean = false;
  links: Link[] = [];
  case:Case|undefined = new Case()
  theme:string = "dark"
  searchText = new FormControl('');
  mobileMode:boolean = false

  constructor(private router: Router,
              private route: ActivatedRoute,
              private navigationService:NavigationService,
              private aetherOne: AetherOneService) {
  }

  ngOnInit() {

    this.theme = localStorage.getItem('theme') ?? 'light';
    document.documentElement.setAttribute('data-bs-theme',this.theme)

    if (this.isMobileDevice()) {
      console.log('mobile device')
      this.mobileMode = true
      this.navigate('MOBILE')
    } else {
      console.log('desktop or laptop device')
      this.mobileMode = false
    }

    this.ping()
    this.initLinks()
    this.navigationService.navigate.subscribe( (url:string) => {
      this.navigate(url);
    });
    // @ts-ignore
    this.theme = localStorage.getItem('theme')
    this.aetherOne.case$.subscribe(value => {
      this.case = value
    })
  }

  navigate(navigationPath: string) {
    this.activateCurrentLink(navigationPath);
    this.router.navigate([navigationPath], {relativeTo: this.route});
  }

  private activateCurrentLink(navigationPath?: string) {

    if (navigationPath?.length === 0) {
      navigationPath = 'DASHBOARD';
    }

    this.links.forEach(link => {
      link.active = false;

      if (link.name === navigationPath) {
        link.active = true;
      }
    });
  }

  private initLinks() {
    this.addLink("MANUAL", false, "#133185", "#fff");
    this.addLink("SETTINGS", false, "#ff9520", "#000");
  }

  private addLink(name: string, active: boolean, backgroundColor:string, color: string) {
    let link:Link = new Link();
    link.name = name;
    link.active = active;
    link.backgroundColor = backgroundColor;
    link.color = color;
    this.links.push(link)
  }

  isMobileDevice(): boolean {
    // @ts-ignore
    const userAgent = navigator.userAgent || navigator.vendor || window['opera'];
    const mobileRegex = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i;

    return mobileRegex.test(userAgent);
  }


  switchTheme() {
    if (document.documentElement.getAttribute('data-bs-theme') == 'dark') {
      document.documentElement.setAttribute('data-bs-theme','light')
      localStorage.setItem('theme', 'light')
      this.theme = "light"
    }
    else {
      document.documentElement.setAttribute('data-bs-theme','dark')
      localStorage.setItem('theme', 'dark')
      this.theme = "dark"
    }
  }

  search() {

  }

  private ping() {
    this.aetherOne.ping().subscribe({
      next: () => {this.serverOnline = true},
      error: () => {this.serverOnline = false}
    });

    setTimeout(() => {
      this.ping();
    }, 5000);
  }
}
