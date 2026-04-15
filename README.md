# RESTful Product Administration Microservice with Lightweight Web UI

<table align="center">
  <tr>
    <td align="center"><img src="screenshots/ui.png" width="200"/></td>
<!--
    <td align="center"><img src="screenshots/ui.png" width="200"/></td>
    <td align="center"><img src="screenshots/ui.png" width="200"/></td>
-->
  </tr>
  <tr>
    <td align="center"><small>Web UI</small></td>
<!--
    <td align="center"><small>Behave</small></td>
    <td align="center"><small>SonarQube</small></td>
-->
  </tr>
</table>

## Main Features

- Role-based permissions (Admin, Sales Manager, Customer)
- Unit and integration tests (with pytest)
- BDD tests (with Behave and Playwright)
- Static Code Analysis with SonarQube
- JWT-based authentication
- Docker containerization for consistent development and deployment

<div align="center">
    <img src="screenshots/screencast-behave.gif" alt="Running Test Suite - Happy Path">
</div>

## Testing Strategy

### Unit & Integration Tests

```bash
docker-compose exec test pytest tests/ --spec


**Test files cover:**
- Model CRUD operations (`test_models.py`)
- Route endpoints (`test_routes.py`)
- Permission-based access control
- Error handling (404, 400, 401, 403, 409)
- Content-Type validation
- Query parameters (name, category_id, availability)


### BDD Tests

```bash
behave                           # Firefox
behave -D browser=chromium       # Chromium
behave -D browser=webkit         # Safari
behave -D ui=false               # Without UI for CI
```

**Feature scenarios (`features/products.feature`):**
- Server health verification
- Product creation flow (login → fill form → create → retrieve)

**Step implementations:**
- `web_interface_steps.py` - UI interactions
- `initial_data_loading_using_api_steps.py` - API database seeding
