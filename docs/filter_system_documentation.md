# University Course Monitor - Filter System Documentation

## 🎯 Overview
The filter system provides a comprehensive way to search and filter German university courses with real-time updates and integrated university selection.

## 🔧 System Architecture

### Filter Flow
```
User Applies Filters → Filter Courses → Update University Counts → Update University Selector → User Selects University → Show Filtered Courses
```

### Components
1. **Filter Controls**: Degree Type, Tuition Fee, Language
2. **University Selector**: Dynamic dropdown with course counts
3. **Course Table**: Displays filtered results
4. **Statistics**: Real-time counts

## 📊 Filter Options

### 1. Course Type (Degree Filter)
- **All**: Shows all degree types
- **Bachelor's**: B.Sc., Bachelor, B.A., etc.
- **Master's**: M.Sc., Master, M.A., etc.
- **Multiple Selection**: Allows selecting multiple degree types

### 2. Tuition Fee Filter
- **All Fees**: No fee filtering
- **Free (No Tuition)**: Only courses with €0 tuition
- **Up to €500**: Courses with tuition ≤ €500
- **Affordable (Free or ≤€500)**: Combines free and low-cost options

### 3. Language Filter
- **All**: No language filtering
- **English**: English-taught programs only
- **German**: German-taught programs only
- **English or German**: Programs in either language

## 🏛️ University Selector Integration

### Dynamic Updates
- University selector shows only universities with courses matching current filters
- Format: `"University Name (X courses)"`
- Real-time count updates as filters change

### Example Flow
```
1. Filter: Master's + English + Free
2. University Selector Updates: 
   - "TU Munich (15 courses)"
   - "RWTH Aachen (8 courses)"
   - "University of Hamburg (12 courses)"
3. Select University: "TU Munich (15 courses)"
4. Course Table: Shows 15 English Master's programs with no fees from TU Munich
```

## 🔄 Data Flow

### Filter Application Process
1. **User Input**: User selects filter options
2. **Filter Storage**: Filters stored in Node-RED flow context
3. **Course Filtering**: All courses filtered by selected criteria
4. **University Counting**: Count courses per university for filtered results
5. **UI Updates**: 
   - University selector options updated
   - Statistics updated
   - Course table updated (if showing filtered results)

### University Selection Process
1. **University Selection**: User selects university from filtered list
2. **Course Filtering**: Courses filtered by university AND existing filters
3. **Display**: Filtered courses displayed in table

## 🛠️ Technical Implementation

### Key Functions

#### `apply_filters`
- Processes filter changes
- Applies degree, fee, and language filters
- Updates university counts
- Returns filtered data to UI components

#### `filter_courses_by_university`
- Handles university selection
- Applies university filter + existing filters
- Formats course data for display

#### `reset_filter_values`
- Resets all filters to default
- Restores original university list
- Clears course table

### Data Structure
```javascript
// Course Object
{
  program_name: "Computer Science",
  institution: "TU Munich",
  degree: "M.Sc.",
  language: "English",
  tuition_fee: 0,
  tuition_period: "semester",
  location: "Munich"
}

// Filter Object
{
  degree: ['master'],
  fee: 'no_fee',
  language: 'english'
}
```

## 🎨 User Experience

### Workflow
1. **Start**: All universities and courses visible
2. **Apply Filters**: University list narrows, counts update
3. **Select University**: View courses from that university matching filters
4. **Refine**: Adjust filters to see different results
5. **Reset**: Clear all filters to start over

### Visual Feedback
- University counts update in real-time
- Filter status preserved during navigation
- Clear messaging when no results found
- Responsive design for different screen sizes

## 🐛 Fixed Issues

### Previous Problems
1. ❌ University selector showing raw data structure
2. ❌ Course table ignoring applied filters
3. ❌ Incorrect tuition fee filtering logic
4. ❌ Inconsistent field name handling

### Solutions Implemented
1. ✅ Fixed Node-RED dropdown format (`msg.options`)
2. ✅ University selection now respects active filters
3. ✅ Improved fee filtering with numeric comparison
4. ✅ Standardized field name handling across components

## 📈 Performance Optimizations

- Course table limited to 100 results for performance
- Efficient filtering using JavaScript array methods
- Cached filter state in Node-RED flow context
- Minimal UI updates to reduce flicker

## 🔮 Future Enhancements

### Planned Features
- [ ] Advanced search with text input
- [ ] Date range filtering for start dates
- [ ] Location-based filtering
- [ ] Saved filter presets
- [ ] Export filtered results
- [ ] Course comparison feature

### Technical Improvements
- [ ] Pagination for large result sets
- [ ] Search result highlighting
- [ ] Filter combination analytics
- [ ] Performance monitoring
