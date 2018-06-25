#Voting Rights Data Institute, June 2018
#Zach Levitt and Ethan Ackerman

library(shiny)
library(maps)
library(mapproj)
library(leaflet)
library(RColorBrewer)
library(tigris)
library(sf)

#Retrieve state boundaries and merge with state rules file
states <- states(cb = TRUE)
states <- states[(states$NAME != "Commonwealth of the Northern Mariana Islands"),]
states <- states[(states$NAME != "United States Virgin Islands"),]
states <- states[(states$NAME != "District of Columbia"),]
states <- states[(states$NAME != "Guam"),]
states <- states[(states$NAME != "American Samoa"),]
states <- states[(states$NAME != "Puerto Rico"),]
states <- states[order(states$NAME),]

stateRules <- read.csv("data/stateRules.csv")
statesAll <- merge(states, stateRules, by="NAME", all.x = FALSE)


#Define equal area projection
epsg2163 <- leafletCRS(
  crsClass = "L.Proj.CRS",
  code = "EPSG:2163",
  proj4def = "+proj=laea +lat_0=45 +lon_0=-100 +x_0=0 +y_0=0 +a=6370997 +b=6370997 +units=m +no_defs",
  resolutions = 2^(16:7))


#HTML code for labeling
labels <- sprintf(
  "<strong>%s</strong>
  <br/>Contiguity: <strong>%s</strong>
  <br/>Equal Population: <strong>%s</strong>
  <br/>Compact Districts: <strong>%s</strong>
  <br/>Political Boundaries: <strong>%s</strong>
  <br/>Communities of Interest: <strong>%s</strong>
  <br/>Prohibit Favoritism: <strong>%s</strong>
  <br/>Competitive Districts: <strong>%s</strong>
  <br/>Source: <a href=%s>link</a>",
  statesAll$NAME, 
  statesAll$Contgty, 
  statesAll$Mtn_Eq_Pop, 
  statesAll$Drw_Cmp_Dis,
  statesAll$Flw_Pol_Bnds_B,
  statesAll$Prsv_Com_B,
  statesAll$Prhbt_Fav_B,
  statesAll$Cmptv_Dis_B,
  statesAll$Links) %>% lapply(htmltools::HTML)

labels2 <- sprintf(
  "<strong>%s</strong>",
  statesAll$NAME) %>% lapply(htmltools::HTML)


# Define UI ----
ui <- fluidPage(
  
  tags$head(
    tags$style(HTML("
                    @import url('//fonts.googleapis.com/css?family=Tajawal');

                    h1 {
                    font-family: 'Tajawal';
                    font-weight: 500;
                    line-height: 1.1;
                    color: #2D5E8E;
                    text-align: center;
                    }

                    .leaflet-container {
                      background: #EAEAEA;
                    }

                    p {
                    font-family: 'Tajawal';
                    font-weight: 100;
                    line-height: 1.4;
                    }

                    h4 {
                    font-family: 'Tajawal';
                    font-weight: 500;
                    line-height: 1.4;
                    font-size: 14px;
                    }

                    .leaflet-popup-content-wrapper .leaflet-popup-content {
                    font-family: 'Tajawal';
                    font-size: 14px;
                    color: #2463A5;
                    }
                    "))
    ),
  
  headerPanel("Congressional Redistricting Laws by State"),
  sidebarLayout(
    position = "left",
    sidebarPanel(
      h4("This interactive map highlights which laws each state follows during redistricting. Although some redistricting laws are federally mandated, such as the Voting Rights Act, 
       each state has control over many aspects of the redistricting process."),
      br(),
      p("Click on a state to view a summary of its congressional redistricting laws."),
      br(),
      p("Choose a variable on the menu to view the national distribution."),
      width = 3
    ),
    
    mainPanel(
      leafletOutput("map", width = "100%", height = 500),
      width = 9
    )
  )
)

# Define server logic ----
server <- function(input, output) {
  output$map <- renderLeaflet({
    factpal <- colorFactor(palette = c("#9CBCDE", "#E1E1E1", "#427CB9"), domain = statesAll$Drw_Cmp_Dis_B)

    leaflet(states, options = leafletOptions(crs = epsg2163)) %>%
      setView(-90, 37.8, 3) %>%

      addPolygons(#CONTIGUITY
        fillColor = ~factpal(statesAll$Contgty_B),
        weight = 1,
        color = "white",
        fillOpacity = 1,
        group = "Contiguity",
        highlight = highlightOptions(
          fillOpacity = 1,
          bringToFront = TRUE),
        label = labels2,
        labelOptions = labelOptions(
          style = list("font-weight" = "normal", padding = "3px 8px"),
          textsize = "13px",
          direction = "auto")) %>%
      
      addPolygons(#FEDERAL RULES
        fillColor = ~factpal(statesAll$Mtn_Eq_Pop_B),
        weight = 1,
        color = "white",
        fillOpacity = 1,
        group = "Federal Rules",
        highlight = highlightOptions(
          fillOpacity = 1,
          fillColor = "#2B639C",
          bringToFront = TRUE),
        label = labels2,
        labelOptions = labelOptions(
          style = list("font-weight" = "normal", padding = "3px 8px"),
          textsize = "13px",
          direction = "auto"),
        popup = labels,
        popupOptions = labelOptions(
          style = list("font-weight" = "normal", padding = "3px 8px"),
          textsize = "13px",
          direction = "auto")) %>%
      
      addPolygons(#COMPACT DISTRICTS
        fillColor = ~factpal(statesAll$Drw_Cmp_Dis_B),
        weight = 1,
        fillOpacity = 1,
        color = "white",
        group = "Compact Districts",
        highlight = highlightOptions(
          fillOpacity = 1,
          bringToFront = TRUE),
        label = labels2,
        labelOptions = labelOptions(
          style = list("font-weight" = "normal", padding = "3px 8px"),
          textsize = "13px",
          direction = "auto")) %>%
      
      addPolygons(#POLITICAL BOUNDARIES
        fillColor = ~factpal(statesAll$Flw_Pol_Bnds_B),
        weight = 1,
        color = "white",
        fillOpacity = 1,
        group = "Political Boundaries",
        highlight = highlightOptions(
          fillOpacity = 1,
          bringToFront = TRUE),
        label = labels2,
        labelOptions = labelOptions(
          style = list("font-weight" = "normal", padding = "3px 8px"),
          textsize = "13px",
          direction = "auto")) %>%
      
      addPolygons(#COMMUNITIES OF INTEREST
        fillColor = ~factpal(statesAll$Prsv_Com_B),
        weight = 1,
        color = "white",
        fillOpacity = 1,
        group = "Communities of Interest",
        highlight = highlightOptions(
          fillOpacity = 1,
          bringToFront = TRUE),
        label = labels2,
        labelOptions = labelOptions(
          style = list("font-weight" = "normal", padding = "3px 8px"),
          textsize = "13px",
          direction = "auto")) %>%
      
      addPolygons(#FAVORITISM
        fillColor = ~factpal(statesAll$Prhbt_Fav_B),
        weight = 1,
        color = "white",
        fillOpacity = 1,
        group = "Prohibit Favoritism",
        highlight = highlightOptions(
          fillOpacity = 1,
          bringToFront = TRUE),
        label = labels2,
        labelOptions = labelOptions(
          style = list("font-weight" = "normal", padding = "3px 8px"),
          textsize = "13px",
          direction = "auto")) %>%
      
      addPolygons(#COMPETITIVE
        fillColor = ~factpal(statesAll$Cmptv_Dis_B),
        weight = 1,
        color = "white",
        fillOpacity = 1,
        group = "Competitive Districts",
        highlight = highlightOptions(
          fillOpacity = 1,
          bringToFront = TRUE),
        label = labels2,
        labelOptions = labelOptions(
          style = list("font-weight" = "normal", padding = "3px 8px"),
          textsize = "13px",
          direction = "auto")) %>%
      
      addLayersControl(
        baseGroups = c( "Federal Rules",
                        "Contiguity",
                        "Compact Districts",
                        "Political Boundaries",
                        "Communities of Interest",
                        "Prohibit Favoritism",
                        "Competitive Districts"
                        ),
        options = layersControlOptions(collapsed = FALSE, position = "bottomright")) %>%
      addLegend(pal = factpal, values = statesAll$Drw_Cmp_Dis_B, opacity = 1, NULL, position = "bottomleft")
      })}


# Run the app ----
shinyApp(ui = ui, server = server)