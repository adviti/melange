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
                <span class="title">Create a new task</span>
                <span class="req">* fields required</span>
            </div>
            
        	<form action="#" method="post" class="form-create-task clearfix">
        		<fieldset id="fieldset-error">
	    			<div class="form-row error form-row-task-title">
	    			    <label for="task-title" class="form-label">Task title<em>*</em> <span class="form-row-error-msg">*Task needs a name!</span></label>
	    			    <input name="task-title" value="" type="text">
	    			</div>
    			</fieldset>
    			<fieldset id="fieldset-task-short-description">
	        		<div class="form-row form-row-task-short-description">
	    			    <label for="short-description" class="form-label">Short description</label>
	    			    <input name="short-description" value="" type="text">
	    				<span class="note">300 characters remaining</span>
	        		</div>
	        	</fieldset>
	        	<fieldset id="fieldset-task-type-tags">
	        	    <div class="form-row grid_4 alpha form-row-task-type">
	        	        <label for="type" class="form-label">Type<em>*</em></label>
	        	        <span class="note">The kind of work to be done</span>
	        	        <div class="form-checkboxes">
	        	            <div class="form-checkboxes-item">
	        	                <input name="code" id="code" value="1" type="checkbox"> <label for="code">Code</label>
	        	            </div>
	        	            <div class="form-checkboxes-item">
	            	            <input name="documentation" id="documentation" value="1" type="checkbox"> <label for="documentation">Documentation</label>
	            	        </div>
	            	        <div class="form-checkboxes-item">
	            	            <input name="outreach" id="outreach" value="1" type="checkbox"> <label for="outreach">Outreach</label>
	            	        </div>
	            	        <div class="form-checkboxes-item">
	            	            <input name="quality" id="quality" value="1" type="checkbox"> <label for="quality">Quality Assurance</label>
	            	        </div>
	            	        <div class="form-checkboxes-item">
	            	            <input name="research" id="research" value="1" type="checkbox"> <label for="research">Research</label>
	            	        </div>
	            	        <div class="form-checkboxes-item">
	            	            <input name="training" id="training" value="1" type="checkbox"> <label for="training">Training</label>
	            	        </div>
	            	        <div class="form-checkboxes-item">
	            	            <input name="translation" id="translation" value="1" type="checkbox"> <label for="translation">Translation</label>
	            	        </div>
	            	        <div class="form-checkboxes-item">
	            	            <input name="ui" id="ui" value="1" type="checkbox"> <label for="ui">User Interface</label>
	            	        </div>
	        	        </div>
	        	    </div>
	
	        	    <div class="form-row grid_4 omega form-row-task-tags">
	        	        <label for="tags" class="form-label">Tags<em>*</em></label>
	        	        <input name="tags" value="" type="text">
	        	        <span class="note">Describe this task with tags (comma separated). Ex: Linux, Apache, C++, GUI</span>
	        	    </div>
        	    </fieldset>

				<fieldset id="fieldset-task-long-description">
	        	    <div class="form-row form-row-task-long-description">
	        	        <label for="long-description" class="form-label">Long description</label>
	        	        <textarea id="long-description" name="long-description"></textarea>
	        	        <span class="note">30,000 characters remaining</span>
	        	    </div>
	        	</fieldset>
        	
        		<fieldset id="fieldset-task-details">
	        	    <div class="form-row form-row-task-completion-time">
	        	        <label for="complete-time" class="form-label">Time to complete<em>*</em></label>
	        	        <div class="form-row-task-completion-time-inner">
	            	        <input name="complete-days" value="" type="text"> days
	            	        <input name="complete-hours" value="" type="text"> hours
	        	        </div>
	        	        <span class="note">30,000 characters remaining</span>
	        	    </div>
	        	
	        	    <div class="form-row form-row-task-difficulty">
	        	        <label for="long-description" class="form-label">Difficulty<em>*</em></label>
	        	        <div class="form-row-task-difficulty-inner">
	            	        <select class="uniform">
	            	        	<option>Select</option>
	            	        	<option>Easy</option>
	            	        	<option>Medium</option>
	            	        	<option>Difficult</option>
	            	        </select class="uniform">
	        	        </div>
	        	        <span class="note">The overall difficulty of the task</span>
	        	    </div>
	        	
	        	    <div class="form-row form-row-task-assigned-mentor">
	        	        <label for="long-description" class="form-label">Assigned Mentor<em>*</em></label>
	        	        <div class="form-row-task-assigned-mentor-inner">
	            	        <select class="uniform">
	            	            <option>Select a mentor</option>
	            	        	<option>Bill Atkinson</option>
	            	        	<option>Mentor name, it's a long one!</option>
	            	        	<option>Mentor name</option>
	            	        	<option>Mentor name</option>
	            	        </select>
	            	        <div class="add-field-link clearfix">
	            	            <a href="javascript:void(0)">+ add another mentor</a>
	            	        </div>
	        	        </div>
	        	        <span class="note">Mentor who will oversee task's completion</span>
	        	    </div>
	        	</fieldset>
        	    
        	    <div class="form-row form-row-buttons">
        	    	<input value="Submit" class="button" type="submit">
        	    </div>
        	</form>
        	
        </div>
        <!-- end .block.block-user-message -->
    </div>
    <!-- end .grid_9.main -->

<?php include '../includes/footer.php'?>