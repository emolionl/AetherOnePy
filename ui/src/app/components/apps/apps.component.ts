import { Component , OnInit } from '@angular/core';
import {AetherOneService} from "../../services/aether-one.service";
import {Toast, ToastrService} from "ngx-toastr";
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
declare var window: any;

@Component({
    selector: 'app-apps',
    templateUrl: './apps.component.html',
    styleUrls: ['./apps.component.scss'],
    standalone: false
})
export class AppsComponent implements OnInit {

  apps = []
  plugins = []
  selectedPlugin: any = null;
  selectedPluginUrl: SafeResourceUrl | null = null;

  constructor(
    private aether: AetherOneService,
    private toast: ToastrService,
    private sanitizer: DomSanitizer
  ) { }

  ngOnInit(): void {
    this.apps.push(
      {name: 'Radionics Device Base 44', route: 'RADIONICS_DEVICE_BASE44', image: 'assets/images/radionicsDeviceBased44.jpg', description: 'Base 44 Radionics Device based on Benjamin Ludwig\'s design'},
      {name: 'Radionics Cards', route: 'CARDS', image: 'assets/images/radionicsCards.png', description: 'Make radionics cards'},
    );
    this.aether.loadPlugins().subscribe({"next": (data) => {
      this.plugins = data.plugins;
    }, "error": (err) => {this.toast.error("Error loading plugins: " + err.message, "Error", {timeOut: 5000})} })

    // Listen for modal close to clear selectedPlugin
    if (typeof window !== 'undefined' && window.bootstrap) {
      setTimeout(() => {
        const modalEl = document.getElementById('pluginModal');
        if (modalEl) {
          modalEl.addEventListener('hidden.bs.modal', () => {
            this.selectedPlugin = null;
          });
        }
      });
    }
  }

  openPluginModal(plugin: any) {
    this.selectedPlugin = plugin;
    console.log('Opening plugin UI:', plugin.ui);
    this.selectedPluginUrl = this.sanitizer.bypassSecurityTrustResourceUrl('/' + plugin.ui);
    setTimeout(() => {
      const modal = new window.bootstrap.Modal(document.getElementById('pluginModal'));
      modal.show();
    });
  }
  
  clearSelectedPlugin() {
    this.selectedPlugin = null;
    this.selectedPluginUrl = null;
  }

  getPluginUrl(plugin: any): SafeResourceUrl {
    return this.sanitizer.bypassSecurityTrustResourceUrl('/' + plugin.ui);

    // For debugging: load a static text file instead of the plugin UI
    //return this.sanitizer.bypassSecurityTrustResourceUrl('assets/test.txt');
  }
}
