export const AWS_GRAPH = `
    <div class="form-group col-sm-12">
        <div class="form-group col-sm-2" style="margin-top: 1%;">
            <div class="form-group">
                <label class="form-label">Interval: </label>
                <select class="form-control" name="graph_time" id="graph_time">
                    <option value="15">15 Minutes</option>
                    <option value="60">1 Hour</option>
                    <option value="360">6 Hours</option>
                    <option value="1440" selected>1 Day</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Period: </label>
                <select class="form-control" name="graph_duration" id="graph_duration">
                    <option value="1">1 Hour</option>
                    <option value="3">3 Hours</option>
                    <option value="6">6 Hours</option>
                    <option value="24">1 Day</option>
                    <option value="72">3 Days</option>
                    <option value="168" selected>1 Week</option>
                    <option value="336">2 Weeks</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Statistic: </label>
                <select class="form-control" name="graph_type" id="graph_type">
                    <option value="average" selected>Average</option>
                    <option value="minimum">Minimum</option>
                    <option value="maximum">Maximum</option>
                    <option value="sum">Sum</option>
                    <option value="sample_count">Data Samples</option>
                </select>
            </div>
        </div>
        <div class="form-group col-sm-10" style="margin-top: 1%;">
            <div id="graph_container" class="form-group" style="display: flex;">
            </div>
        </div>
    </div>
`

export const AZURE_GRAPH = `
    <div class="form-group col-sm-2" style="margin-top: 1%;">
        <div class="form-group">
            <label class="form-label">Time Granularity: </label>
            <select class="form-control" name="graph_time" id="graph_time">
                <option value="5-minutes">5 Minutes</option>
                <option value="15-minutes">15 Minutes</option>
                <option value="30-minutes">30 Minutes</option>
                <option value="1-hour">1 Hour</option>
                <option value="6-hours">6 Hours</option>
                <option value="12-hours">12 Hours</option>
                <option value="1-day" selected>1 Day</option>
                <option value="1-week">1 Week</option>
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">Period: </label>
            <select class="form-control" name="graph_duration" id="graph_duration">
                <option value="1-hour">1 Hour</option>
                <option value="3-hours">3 Hours</option>
                <option value="6-hours">6 Hours</option>
                <option value="1-day">1 Day</option>
                <option value="3-days">3 Days</option>
                <option value="1-week" selected>1 Week</option>
                <option value="2-weeks">2 Weeks</option>
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">Aggregation: </label>
            <select class="form-control" name="graph_type" id="graph_type">
                <option value="average" selected>Average</option>
                <option value="count">Count</option>
                <option value="minimum">Minimum</option>
                <option value="maximum">Maximum</option>
                <option value="total">Total</option>
            </select>
        </div>
    </div>
    <div class="form-group col-sm-10" style="margin-top: 1%;">
        <div id="graph_container" class="form-group" style="display: flex;">
        </div>
    </div>
`