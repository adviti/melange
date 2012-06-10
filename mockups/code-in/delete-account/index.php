<?php include '../includes/header.php'?>

    <div class="grid_3 side">
        <div class="block block-main-nav">
            <ul class="menu">
                <li><a href="javascript:void(0)">My Dashboard</a>
                    <ul>
                        <li class="active"><a href="javascript:void(0)">Create a new task</a></li>
                    </ul>
                </li>
                <li><a href="javascript:void(0)">About Us</a></li>
                <li><a href="javascript:void(0)">Get Started</a></li>
                <li><a href="javascript:void(0)">Participating Organizations</a></li>
                <li><a href="javascript:void(0)">Blog</a></li>
            </ul>
        </div>
        <!-- end .block.block-main-nav -->
        
        <div class="block block-status block-status-sm">
            <div class="block-status-user">
                You are logged in as: <a href="javascript:void(0)">eric_schmidt@gmail.com</a> <a href="javascript:void(0)">(change)</a>
            </div>
            <div class="block-status-action block-status-action-single clearfix">
                <a href="javascript:void(0)" class="block-status-action-dashboard"><span>My Dashboard</span></a>
            </div>
        </div>
        <!-- end .block.block-status.block-status-sm -->
    </div>
    <!-- end .grid_3.side -->
    <div class="grid_9 main">
        <div class="block block-user-message">
            Well, you've broken something. <a href="javascript:void(0)" class="more">Read more</a>
        </div>
        <!-- end .block.block-user-message -->
        <div class="block block-form">
            <div class="block-form-title">
                <span class="title">Page title</span>
                <span class="req">* fields required</span>
            </div>
            
        	<form action="#" method="post" class="clearfix">
    			<div class="form-row error form-row-task-title">
    			    <label for="error-field" class="form-label">Error message<em>*</em> <span class="form-row-error-msg">*Don't do that!</span></label>
    			    <input name="error-field" value="" type="text">
    			</div>
        		<div class="form-row">
    			    <label for="regular-text-field" class="form-label">Regular form row</label>
    			    <input name="regular-text-field" value="" type="text">
    				<span class="note">300 characters remaining, this is a note</span>
        		</div>

        	    <div class="form-row grid_4 alpha">
        	        <label for="type" class="form-label">Half column, checkboxes<em>*</em></label>
        	        <div class="form-checkbox">
        	            <div class="form-checkbox-item">
        	                <input name="code" id="code" value="1" type="checkbox"> <label for="code">Code</label>
        	            </div>
        	            <div class="form-checkbox-item">
            	            <input name="documentation" id="documentation" value="1" type="checkbox"> <label for="documentation">Documentation</label>
            	        </div>
            	        <div class="form-checkbox-item">
            	            <input name="outreach" id="outreach" value="1" type="checkbox"> <label for="outreach">Outreach</label>
            	        </div>
            	        <div class="form-checkbox-item">
            	            <input name="quality" id="quality" value="1" type="checkbox"> <label for="quality">Quality Assurance</label>
            	        </div>
            	        <div class="form-checkbox-item">
            	            <input name="research" id="research" value="1" type="checkbox"> <label for="research">Research</label>
            	        </div>
            	        <div class="form-checkbox-item">
            	            <input name="training" id="training" value="1" type="checkbox"> <label for="training">Training</label>
            	        </div>
            	        <div class="form-checkbox-item">
            	            <input name="translation" id="translation" value="1" type="checkbox"> <label for="translation">Translation</label>
            	        </div>
            	        <div class="form-checkbox-item">
            	            <input name="ui" id="ui" value="1" type="checkbox"> <label for="ui">User Interface</label>
            	        </div>
        	        </div>
        	    </div>

        	    <div class="form-row grid_4 omega">
        	        <label for="half-text-field" class="form-label">Half column, text field<em>*</em></label>
        	        <input name="half-text-field" value="" type="text">
        	        <span class="note">Put a note on it</span>
        	    </div>
        	    
        	    <div class="clear"></div>

        	    <div class="form-row">
        	        <label for="full-textarea" class="form-label">Regular form row, textarea</label>
        	        <textarea id="full-textarea" name="full-textarea"></textarea>
        	        <span class="note">Don't forget the WYSIWYG!</span>
        	    </div>
        	    
        	    <div class="form-row grid_4 alpha">
        	        <label for="half-textarea" class="form-label">Half column, textarea<em>*</em></label>
        	        <textarea id="half-textarea" name="half-textarea"></textarea>
        	    </div>
        	    
        	    <div class="form-row grid_4 omega">
        	        <label for="type" class="form-label">Radios<em>*</em></label>
        	        <div class="form-radio">
        	            <div class="form-radio-item">
        	                <input name="radio1" id="radio1" value="1" type="radio"> <label for="radio1">Option 1</label>
        	            </div>
        	            <div class="form-radio-item">
        	                <input name="radio1" id="radio2" value="1" type="radio"> <label for="radio2">Option 2</label>
        	            </div>
        	            <div class="form-radio-item">
        	                <input name="radio1" id="radio3" value="1" type="radio"> <label for="radio3">Option 3</label>
        	            </div>
        	        </div>
        	    </div>
        	    
        	    <div class="clear"></div>
        	    
        	    <div class="form-row grid_4 alpha">
        	        <label for="half-text-field" class="form-label">Half column, text field<em>*</em></label>
        	        <input name="half-text-field" value="" type="text">
        	    </div>
        	    
        	    <div class="form-row grid_4 omega">
        	        <label for="half-textarea" class="form-label">Half column, textarea<em>*</em></label>
        	        <textarea id="half-textarea" name="half-textarea"></textarea>
        	    </div>
        	    
        	    <div class="form-row form-row-buttons">
        	    	<input value="Save" class="button" type="submit">
        	    	<input value="Discard" class="button" type="button">
        	    	<input value="Delete Account" class="delete-btn" type="button" />
        	    </div>
        	    
        	</form>
        	
        </div>
        <!-- end .block.block-user-message -->
    </div>
    <!-- end .grid_9.main -->

<?php include '../includes/footer.php'?>