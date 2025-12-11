# Better11 - Week 5 Development Plan

**Date**: December 10, 2025  
**Sprint**: Week 5 (Services, GUI Expansion, Testing)  
**Status**: 🚀 **IN PROGRESS**  
**Previous Completion**: 77%  
**Target Completion**: 82%

---

## 🎯 Week 5 Objectives

Based on project progress (77% complete), Week 5 focuses on:

1. **Services Support in Startup Manager** - Complete startup management
2. **GUI Expansion** - Add Privacy and Performance tabs
3. **Additional Pester Tests** - Cover more PowerShell modules
4. **PowerShell Gallery Prep** - Create module manifest
5. **Polish & Documentation** - Update guides

**Goal**: Reach 82% completion (+5%), deliver complete startup management, expand GUI

---

## 📋 Detailed Tasks

### 1. Services Support in Startup Manager ⭐ HIGH PRIORITY

**Status**: 🔄 IN PROGRESS

**Objective**: Add Windows Services that run at startup to the Startup Manager

**Python Implementation** (`system_tools/startup.py`):
- [ ] Add `SERVICES` to `StartupLocation` enum
- [ ] Implement `_get_startup_services()` method
- [ ] Filter for automatic/automatic-delayed services
- [ ] Add enable/disable/configure service operations
- [ ] Integrate into `list_startup_items()`
- [ ] Add to CLI commands
- [ ] Write tests

**PowerShell Implementation** (`SystemTools/StartupManager.psm1`):
- [ ] Implement `GetStartupServices()` method
- [ ] Add to `ListStartupItems()`
- [ ] Implement service configuration methods
- [ ] Integrate into CLI

**Technical Approach**:
```python
# Python - Use subprocess with sc.exe or direct Windows API
def _get_startup_services(self) -> List[StartupItem]:
    """Get services set to start automatically."""
    # Query: Get-Service | Where-Object {$_.StartType -eq 'Automatic'}
    # Return as StartupItem with SERVICES location
```

**Estimated Effort**: 4-6 hours  
**Tests**: 15+ new tests  
**Impact**: Complete startup management (all locations)

---

### 2. GUI Privacy Settings Tab ⭐ HIGH PRIORITY

**Status**: ⏳ PENDING

**Objective**: Add Privacy Settings management to GUI

**Implementation** (`better11/gui_tkinter.py`):
- [ ] Create `create_privacy_tab()` method
- [ ] List privacy settings (telemetry, advertising ID, etc.)
- [ ] Show current status (enabled/disabled)
- [ ] Add Apply/Reset buttons
- [ ] Integrate with `system_tools.privacy` module
- [ ] Add logging of changes
- [ ] Update GUI_README.md

**Features**:
- Telemetry level (Off, Basic, Enhanced, Full)
- Advertising ID (On/Off)
- Location tracking (On/Off)
- Activity history (On/Off)
- Diagnostic data (On/Off)
- Feedback frequency
- Cortana
- WiFi Sense
- Windows Tips

**UI Design**:
```
┌─ Privacy Settings ────────────────────────────────────┐
│                                                        │
│ ┌─ Telemetry & Data Collection ──────────────────┐   │
│ │ ○ Security (Minimum)                           │   │
│ │ ○ Basic                                        │   │
│ │ ○ Enhanced                                     │   │
│ │ ○ Full                                         │   │
│ └────────────────────────────────────────────────┘   │
│                                                        │
│ ┌─ Privacy Controls ──────────────────────────────┐   │
│ │ [✓] Disable Advertising ID                     │   │
│ │ [✓] Disable Location Tracking                  │   │
│ │ [✓] Disable Activity History                   │   │
│ │ [ ] Disable Cortana                            │   │
│ │ [✓] Disable Windows Tips                       │   │
│ └────────────────────────────────────────────────┘   │
│                                                        │
│ [Apply Settings] [Reset to Defaults] [Show Details]   │
└────────────────────────────────────────────────────────┘
```

**Estimated Effort**: 6-8 hours  
**Impact**: Major GUI expansion, high user value

---

### 3. GUI Performance Tab ⭐ MEDIUM PRIORITY

**Status**: ⏳ PENDING

**Objective**: Add Performance optimization to GUI

**Implementation** (`better11/gui_tkinter.py`):
- [ ] Create `create_performance_tab()` method
- [ ] Show current performance preset
- [ ] Add preset selector (Maximum, Balanced, Quality)
- [ ] Visual effects controls
- [ ] Power plan management
- [ ] SSD optimization
- [ ] Apply changes with confirmation

**Features**:
- Performance presets (Maximum, Balanced, Quality)
- Visual effects (checkboxes for individual settings)
- Power plan selection
- System responsiveness
- SSD optimization (TRIM, indexing, etc.)
- Boot time display

**UI Design**:
```
┌─ Performance Optimization ────────────────────────────┐
│                                                        │
│ Current Boot Time: 45 seconds (🟡 Medium)             │
│                                                        │
│ ┌─ Performance Preset ────────────────────────────┐   │
│ │ ○ Maximum Performance                          │   │
│ │ ● Balanced                                     │   │
│ │ ○ Best Appearance                              │   │
│ └────────────────────────────────────────────────┘   │
│                                                        │
│ ┌─ Visual Effects ────────────────────────────────┐   │
│ │ [✓] Animate windows when minimizing/maximizing │   │
│ │ [ ] Fade or slide menus into view              │   │
│ │ [✓] Show shadows under windows                 │   │
│ │ [ ] Slide open combo boxes                     │   │
│ │ [✓] Smooth-scroll list boxes                   │   │
│ └────────────────────────────────────────────────┘   │
│                                                        │
│ Power Plan: [High Performance ▼]                      │
│                                                        │
│ [Apply Preset] [Customize] [Reset]                    │
└────────────────────────────────────────────────────────┘
```

**Estimated Effort**: 6-8 hours  
**Impact**: Major GUI expansion, developer-focused

---

### 4. Additional Pester Tests ⭐ MEDIUM PRIORITY

**Status**: ⏳ PENDING

**Objective**: Expand PowerShell test coverage

**Test Files to Create**:
- [ ] `Tests/Privacy.Tests.ps1` (20+ tests)
- [ ] `Tests/Services.Tests.ps1` (20+ tests)
- [ ] `Tests/Performance.Tests.ps1` (20+ tests)
- [ ] `Tests/Features.Tests.ps1` (15+ tests)
- [ ] `Tests/Registry.Tests.ps1` (15+ tests)

**Test Coverage Goals**:
- Privacy settings (get, set, reset)
- Services (list, optimize, configure)
- Performance presets and settings
- Windows features (list, enable, disable)
- Registry tweaks (apply, validate)

**Example Test Structure**:
```powershell
# Tests/Privacy.Tests.ps1
Describe "Privacy Module Tests" {
    Context "Privacy Settings" {
        It "Should list privacy settings" {
            $settings = Get-PrivacySettings
            $settings | Should -Not -BeNullOrEmpty
        }
        
        It "Should get telemetry level" {
            $level = Get-TelemetryLevel
            $level | Should -BeIn @('Security', 'Basic', 'Enhanced', 'Full')
        }
        
        It "Should disable advertising ID in dry-run" {
            Set-PrivacySetting -Setting DisableAdvertisingId -DryRun
            # Verify no changes made
        }
    }
    
    Context "Privacy Manager Class" {
        It "Should create PrivacyManager" {
            $manager = [PrivacyManager]::new()
            $manager | Should -Not -BeNullOrEmpty
        }
    }
}
```

**Estimated Effort**: 8-10 hours  
**Impact**: ~90+ Pester tests total, comprehensive coverage

---

### 5. PowerShell Module Manifest ⭐ HIGH PRIORITY

**Status**: ⏳ PENDING

**Objective**: Create PowerShell module manifest for Gallery publishing

**Files to Create**:
- [ ] `powershell/Better11.psd1` - Main module manifest
- [ ] `powershell/README.md` update - Gallery description
- [ ] `powershell/LICENSE.txt` - License file
- [ ] `powershell/CHANGELOG.md` - Change log

**Manifest Structure**:
```powershell
# Better11.psd1
@{
    # Module Info
    ModuleVersion = '0.3.0'
    GUID = 'GENERATE-NEW-GUID'
    Author = 'Better11 Team'
    CompanyName = 'Better11'
    Copyright = '(c) 2025 Better11. All rights reserved.'
    Description = 'Windows 11 system optimization toolkit with 8+ system tools'
    
    # Requirements
    PowerShellVersion = '7.0'
    CompatiblePSEditions = @('Core', 'Desktop')
    
    # Module Components
    RootModule = 'Better11.psm1'
    NestedModules = @(
        'Better11/Config.psm1',
        'Better11/Interfaces.psm1',
        'SystemTools/Base.psm1',
        'SystemTools/Safety.psm1',
        'SystemTools/StartupManager.psm1',
        'SystemTools/Registry.psm1',
        'SystemTools/Services.psm1',
        'SystemTools/Bloatware.psm1',
        'SystemTools/Privacy.psm1',
        'SystemTools/Features.psm1',
        'SystemTools/Performance.psm1',
        'SystemTools/Updates.psm1'
    )
    
    # Exported Functions
    FunctionsToExport = @(
        'Get-StartupItems', 'Disable-StartupItem', 'Enable-StartupItem',
        'Remove-StartupItem', 'Get-PrivacySettings', 'Set-PrivacySetting',
        'Get-ServiceRecommendations', 'Optimize-Services',
        'Get-BloatwareApps', 'Remove-BloatwareApp',
        'Set-PerformancePreset', 'Get-WindowsFeatures'
    )
    
    # Tags for Gallery
    PrivateData = @{
        PSData = @{
            Tags = @('Windows11', 'Optimization', 'Privacy', 'Performance', 
                    'Startup', 'Services', 'Registry', 'SystemTools')
            LicenseUri = 'https://github.com/better11/better11/blob/main/LICENSE'
            ProjectUri = 'https://github.com/better11/better11'
            IconUri = 'https://better11.io/icon.png'
            ReleaseNotes = 'See CHANGELOG.md'
        }
    }
}
```

**Publishing Steps**:
```powershell
# 1. Test locally
Test-ModuleManifest .\Better11.psd1

# 2. Create package
New-ModuleManifest -Path .\Better11.psd1 @manifestParams

# 3. Publish (when ready)
Publish-Module -Path . -NuGetApiKey $apiKey -Repository PSGallery
```

**Estimated Effort**: 3-4 hours  
**Impact**: Ready for PowerShell Gallery publishing

---

## 📊 Week 5 Metrics

### Target Metrics

| Metric | Current | Week 5 Target | Change |
|--------|---------|---------------|--------|
| **Project Completion** | 77% | 82% | +5% |
| **Python Tests** | 143 | 158+ | +15 |
| **PowerShell Tests** | 40+ | 90+ | +50 |
| **GUI Tabs** | 2 | 4 | +2 |
| **Startup Locations** | 3 | 4 | +1 |
| **Lines of Code** | 11,000 | 12,500+ | +1,500 |
| **Documentation** | 15,800 | 17,000+ | +1,200 |

### Quality Goals

- ✅ 100% test pass rate maintained
- ✅ Zero regressions
- ✅ All new features documented
- ✅ Comprehensive error handling
- ✅ User safety (confirmations, backups)

---

## 🗓 Week 5 Timeline

### Day 1 (Today): Services Support
- ✅ Week 5 plan created
- 🔄 Implement services enumeration (Python)
- 🔄 Implement services enumeration (PowerShell)
- ⏳ Add services to CLI
- ⏳ Write services tests

### Day 2: Complete Services + Start GUI
- ⏳ Complete services integration
- ⏳ Start Privacy tab GUI
- ⏳ Test services functionality

### Day 3: Privacy Tab
- ⏳ Complete Privacy tab UI
- ⏳ Integrate with privacy module
- ⏳ Test privacy operations
- ⏳ Update documentation

### Day 4: Performance Tab
- ⏳ Complete Performance tab UI
- ⏳ Integrate with performance module
- ⏳ Test performance operations
- ⏳ Update documentation

### Day 5: Testing & Manifest
- ⏳ Write additional Pester tests
- ⏳ Create PowerShell manifest
- ⏳ Test module publishing
- ⏳ Documentation updates

---

## 🎯 Success Criteria

### Must Have (P0)
- [x] Week 5 plan created
- [ ] Services support complete (Python + PowerShell)
- [ ] Privacy tab in GUI (functional)
- [ ] Performance tab in GUI (functional)
- [ ] 15+ new Python tests
- [ ] 50+ new Pester tests
- [ ] PowerShell manifest created
- [ ] All tests passing (100% rate)

### Should Have (P1)
- [ ] GUI polish (styling, UX improvements)
- [ ] More comprehensive tests
- [ ] Performance optimizations
- [ ] Additional documentation

### Nice to Have (P2)
- [ ] Dark mode toggle
- [ ] Batch operations
- [ ] Export/import settings
- [ ] System tray icon

---

## 🚀 Getting Started

### Immediate Next Steps (Now)

1. **Add Services to Startup Manager** (Python)
   - Add SERVICES to StartupLocation enum
   - Implement _get_startup_services() method
   - Integrate into list_startup_items()

2. **Test Services Implementation**
   - Write unit tests
   - Manual testing on Windows

3. **Port to PowerShell**
   - Implement GetStartupServices()
   - Add to StartupManager

4. **GUI Development**
   - Create Privacy tab
   - Create Performance tab
   - Test UI/UX

---

## 📚 References

### Related Documents
- `PROJECT_INDEX.md` - Complete project reference
- `WEEK4_COMPLETION_REPORT.md` - Previous sprint results
- `IMPLEMENTATION_PLAN_V0.3.0.md` - Original plan
- `WHATS_NEXT.md` - Strategic direction

### Code References
- `system_tools/startup.py` - Startup manager
- `system_tools/privacy.py` - Privacy module
- `system_tools/services.py` - Services module
- `system_tools/performance.py` - Performance module
- `better11/gui_tkinter.py` - GUI implementation

---

## 🎉 Week 5 Goals Summary

**Primary Goals**:
1. ✅ Complete startup management (add services)
2. ⏳ Expand GUI (Privacy + Performance tabs)
3. ⏳ Increase test coverage (90+ Pester tests)
4. ⏳ Prepare for publishing (PowerShell manifest)

**Expected Outcomes**:
- 82% project completion (+5%)
- 4 GUI tabs (was 2)
- 248+ total tests (was 183)
- PowerShell Gallery ready
- Complete startup management

**Stretch Goals**:
- Dark mode implementation
- Batch operations
- Export/import functionality
- Additional polish

---

**Prepared by**: Better11 Development Team  
**Date**: December 10, 2025  
**Sprint**: Week 5  
**Status**: In Progress  
**Next Review**: End of Week 5

---

*"Week 5: Completing the vision, expanding the interface, preparing for launch! 🚀"*
